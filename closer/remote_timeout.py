import subprocess
import contextlib
import time
from closer import exceptions

class RemoteTimeout:
    def __init__( self, remote, timeout, command, kwargs ):
        self._remote = remote
        self._timeout = timeout
        self._command = command
        self._check = False
        if 'check' in kwargs:
            self._check = kwargs[ 'check' ]
            del kwargs[ 'check' ]

        self._process = subprocess.Popen( self._command, ** kwargs )
        self._wait()

    def _wait( self ):
        self._start = time.time()
        while self._process.poll() is None:
            if self._timedOut():
                with contextlib.suppress( Exception ):
                    self._remote.terminate()
                raise exceptions.RemoteProcessTimeout( 'runtime exceeded {} seconds for remote process: {}'.format( self._timeout, self._remote ) )
            time.sleep( 1 )

        self._checkSuccess()

    def _checkSuccess( self ):
        if not self._check:
            return
        exitCode = self._process.returncode
        if exitCode != 0:
            raise subprocess.CalledProcessError( exitCode, self._command, output = self._safeRead( self._process.stdout ), stderr = self._safeRead( self._process.stderr ) )

    def _safeRead( self, stream ):
        if stream is None:
            return None
        else:
            return stream.read()

    def _timedOut( self ):
        if self._timeout is None:
            return False
        now = time.time()
        return now - self._start > self._timeout

    @property
    def completedProcess( self ):
        return subprocess.CompletedProcess( self._process.args,
                                            self._process.returncode,
                                            stdout = self._safeRead( self._process.stdout ),
                                            stderr = self._safeRead( self._process.stderr ) )
