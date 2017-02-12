import subprocess
import logging
import atexit
import cPickle


class Remote( object ):
    def __init__( self, user, host, ownKwargs, cleanup, closerCommand, * popenArgs, ** popenKwargs ):
        killer = 'terminate'
        if cleanup is not None:
            assert cleanup in [ 'kill', 'terminate' ]
            killer = cleanup
        closer = dict( args = popenArgs, kwargs = popenKwargs )
        hexedPickle = cPickle.dumps( closer ).encode( 'hex' )
        sshCommand = [ 'ssh', '{}@{}'.format( user, host ), closerCommand, '--quit-on-input', '--killer', killer, hexedPickle ]
        self._process = subprocess.Popen( sshCommand, stdin = subprocess.PIPE, ** ownKwargs )
        logging.info( 'pid={} running {}'.format( self._process.pid, sshCommand ) )
        self._terminated = False
        if cleanup is not None:
            atexit.register( self._cleanup )

    def process( self ):
        return self._process

    def _cleanup( self ):
        self.terminate()

    def terminate( self ):
        if self._terminated:
            return
        self._terminated = True
        self._process.communicate( 'x\n' )
