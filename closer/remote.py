import subprocess
import logging
import atexit
import cPickle


class Remote( object ):
    def __init__( self, user, host, * popenArgs, ** popenKwargs ):
        self._user = user
        self._host = host
        self._sshTarget = '{}@{}'.format( self._user, self._host )
        self._ownKwargs = {}
        self._killer = 'terminate'
        self._remotePopenDetails = dict( args = popenArgs, kwargs = popenKwargs )
        self._hexedPickle = cPickle.dumps( self._remotePopenDetails ).encode( 'hex' )
        self._terminated = False
        self._closer = 'closer'

    def localProcessKwargs( self, ** kwargs ):
        self._ownKwargs = kwargs

    @property
    def killer( self ):
        return self._killer

    @killer.setter
    def _setKiller( self, killer ):
        assert killer in [ 'terminate', 'kill' ]
        self._killer = killer

    def setCloserCommand( self, command ):
        self._closer = command

    def background( self, cleanup = False ):
        sshCommand = [ 'ssh', self._sshTarget , self._closer, '--quit-on-input', '--killer', self._killer, self._hexedPickle ]
        self._process = subprocess.Popen( sshCommand, stdin = subprocess.PIPE, ** self._ownKwargs )
        logging.info( 'pid={} running {}'.format( self._process.pid, sshCommand ) )
        if cleanup:
            atexit.register( self.terminate )

    def foreground( self ):
        sshCommand = [ 'ssh', self._sshTarget, self._closer, '--killer', self._killer, self._hexedPickle ]
        return subprocess.check_call( sshCommand, ** self._ownKwargs )

    def output( self ):
        sshCommand = [ 'ssh', self._sshTarget, self._closer, '--killer', self._killer, self._hexedPickle ]
        return subprocess.check_output( sshCommand, ** self._ownKwargs )

    @property
    def process( self ):
        return self._process

    def terminate( self ):
        if self._terminated:
            return
        self._terminated = True
        self._process.communicate( 'x\n' )
