import subprocess
import codecs
import logging
import random
import requests
import atexit
import pickle
import pimped_subprocess

PORT_RANGE = 64000, 65500

class RemoteProcessError( Exception ):
    def __init__( self, popenDetails, causedBy ):
        self.popenDetails = popenDetails
        self.exitCode = causedBy.returncode
        self.causedBy = causedBy
        Exception.__init__( self, 'remote process finished with exit code {}: popenDetails={}'.format( self.exitCode, popenDetails ) )

class Remote( object ):
    _cleanup = []

    @classmethod
    def tidyUp( cls, * args ):
        for remote in cls._cleanup:
            remote.terminate()

    def __init__( self, user, host, * popenArgs, ** popenKwargs ):
        self._user = user
        self._host = host
        random.seed()
        self._port = random.randint( * PORT_RANGE )
        self._sshTarget = '{}@{}'.format( self._user, self._host )
        self._ownKwargs = {}
        self._killer = 'terminate'
        self._remotePopenDetails = dict( args = popenArgs, kwargs = popenKwargs )
        self._terminated = False
        self._closer = 'closer3'
        self._sshPort = 22
        self._sshOptions = ''

    @property
    def sshPort( self ):
        return self._sshPort

    @sshPort.setter
    def sshPort( self, port ):
        self._sshPort = port

    def sshOptions( self, options ):
        self._sshOptions = options

    def __repr__( self ):
        return str( self._remotePopenDetails )

    def _hexedPickle( self ):
        details = dict( popenDetails = self._remotePopenDetails, port = self._port )
        pickled = pickle.dumps( details, protocol = 2 )
        return codecs.encode( pickled, 'hex' )

    def localProcessKwargs( self, ** kwargs ):
        self._ownKwargs = kwargs

    @property
    def killer( self ):
        return self._killer

    @killer.setter
    def _setKiller( self, killer ):
        assert killer in [ 'terminate', 'kill' ]
        self._killer = killer

    def _baseCommand( self ):
        logging.info( 'closer launching remote subprocess: {}'.format( self ) )
        return [ 'ssh', '-o', self._sshOptions, '-p', str( self._sshPort ), self._sshTarget , self._closer, ]

    def setCloserCommand( self, command ):
        self._closer = command

    def background( self, cleanup = False ):
        sshCommand = self._baseCommand() + [ '--quit-when-told', '--killer', self._killer, self._hexedPickle() ]
        self._process = subprocess.Popen( sshCommand, stdin = subprocess.PIPE, ** self._ownKwargs )
        if cleanup:
            Remote._cleanup.append( self )

    def foreground( self, check = True ):
        sshCommand = self._baseCommand() + [ '--killer', self._killer, self._hexedPickle() ]
        try:
            if check:
                return subprocess.check_call( sshCommand, ** self._ownKwargs )
            else:
                return subprocess.call( sshCommand, ** self._ownKwargs )
        except subprocess.CalledProcessError as e:
            raise RemoteProcessError( self._remotePopenDetails, e )

    def output( self, binary = False ):
        sshCommand = self._baseCommand() + [ '--killer', self._killer, self._hexedPickle() ]
        kwargs = dict( self._ownKwargs )
        kwargs[ 'universal_newlines' ] = not binary
        try:
            return subprocess.check_output( sshCommand, ** kwargs )
        except subprocess.CalledProcessError as e:
            raise RemoteProcessError( self._remotePopenDetails, e )

    def liveMonitor( self, onOutput, onProcessEnd = None, cleanup = False ):
        sshCommand = self._baseCommand() + [ '--quit-when-told', '--killer', self._killer, self._hexedPickle() ]
        self._process = pimped_subprocess.PimpedSubprocess( sshCommand, stdin = subprocess.PIPE, ** self._ownKwargs )
        self._process.onOutput( onOutput )
        if onProcessEnd is not None:
            self._process.onProcessEnd( onProcessEnd )
        self._process.launch()
        if cleanup:
            Remote._cleanup.append( self )

    @property
    def process( self ):
        return self._process

    def terminate( self ):
        try:
            logging.info( 'terminating {}'.format( self ) )
            if self._terminated:
                return
            url = 'http://{}:{}/kill'.format( self._host, self._port )
            requests.get( url )
            self._terminated = True
        except requests.exceptions.RequestException as e:
            logging.error( 'exception {} happened while killing {}. This may not be a problem if the process already died on the remote side'.format( e, self ) )

atexit.register( Remote.tidyUp )
