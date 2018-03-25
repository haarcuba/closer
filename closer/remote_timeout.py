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
        try:
            self._output, self._error = self._process.communicate( timeout = self._timeout )
        except subprocess.TimeoutExpired:
            self._remote.terminate()
            raise exceptions.RemoteProcessTimeout( 'runtime exceeded {} seconds for remote process: {}'.format( self._timeout, self._remote ) )

        self._checkSuccess()

    def _checkSuccess( self ):
        if not self._check:
            return
        exitCode = self._process.returncode
        if exitCode != 0:
            raise subprocess.CalledProcessError( exitCode, self._command, output = self._output, stderr = self._error )

    @property
    def completedProcess( self ):
        return subprocess.CompletedProcess( self._process.args,
                                            self._process.returncode,
                                            stdout = self._output,
                                            stderr = self._error )
