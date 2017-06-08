import pytest
import time
import closer.remote
import subprocess
import random

IP = '172.17.0.2'
USER = 'me'

class Monitor( object ):
    def __init__( self ):
        self.output = []
        self.exitCode = None
        self.deathNotification = False

    def onDeath( self, exitCode ):
        self.exitCode = exitCode
        self.deathNotification = True

    def onOutput( self, line ):
        self.output.append( line )

class TestRealLiveProcesses( object ):
    def setup( self ):
        subprocess.call( "ssh {}@{} pkill -f closer".format( USER, IP ), shell = True )

    @pytest.fixture( params = ( 'closer', 'closer3' ) )
    def closerCommand( self, request ):
        return request.param

    def test_sanity( self, closerCommand ):
        tested = closer.remote.Remote( USER, IP, "bash -c 'exit 77'", shell = True )
        tested.setCloserCommand( closerCommand )
        exitCode = tested.foreground( check = False )
        assert exitCode == 77

        tag = str( random.random() )
        tested = closer.remote.Remote( USER, IP, "bash -c 'echo -n {}-{}-{}'".format( tag, tag, tag ), shell = True )
        tested.setCloserCommand( closerCommand )
        output = tested.output()
        assert output.decode( 'ascii' ) == '{}-{}-{}'.format( tag, tag, tag )

    def test_remote_subprocess_dies_when_closer_told_to_quit( self, closerCommand ):
        tag = str( random.random() )
        tested = closer.remote.Remote( USER, IP, "bash -c 'sleep 1000; echo tag={}'".format( tag ), shell = True )
        tested.setCloserCommand( closerCommand )
        tested.background( cleanup = False )
        assert self.processAlive( 'closer' )
        assert self.processAlive( 'tag={}'.format( tag ), slack = 0 )
        tested.terminate()
        assert not self.processAlive( 'tag={}'.format( tag ), slack = 0 )
        assert not self.processAlive( 'closer' )

    def test_many_closer_processes_in_parallel( self, closerCommand ):
        tags = [ str( random.random() ) for _ in range( 10 ) ]
        remotes = {}
        for tag in tags:
            remote = closer.remote.Remote( USER, IP, "bash -c 'sleep 1000; echo tag={}'".format( tag ), shell = True )
            remote.setCloserCommand( closerCommand )
            remote.background( cleanup = False )
            remotes[ tag ] = remote
            assert self.processAlive( 'tag={}'.format( tag ) )

        for tag in tags:
            remote = remotes[ tag ]
            remote.terminate()
            assert not self.processAlive( 'tag={}'.format( tag ) )

        assert not self.processAlive( 'closer' )

    def test_closer_process_dies_if_remote_subprocess_dies( self, closerCommand ):
        tag = str( random.random() )
        tested = closer.remote.Remote( USER, IP, "bash -c 'sleep 3; echo tag={}'".format( tag ), shell = True )
        tested.setCloserCommand( closerCommand )
        tested.background( cleanup = False )
        assert self.processAlive( 'closer' )
        assert self.processAlive( 'tag={}'.format( tag ) )
        LET_PROCESS_DIE_NATURALLY = 2
        time.sleep( LET_PROCESS_DIE_NATURALLY )
        assert not self.processAlive( 'tag={}'.format( tag ) )
        assert not self.processAlive( 'closer' )

    def test_live_monitoring_of_remote_process( self, closerCommand ):
        tag = str( random.random() )
        tested = closer.remote.Remote( USER, IP, "bash -c 'for i in 1 2 3 4 5; do echo {}_$i; sleep 1; done'".format( tag ), shell = True )
        tested.setCloserCommand( closerCommand )
        monitor = Monitor()
        assert not monitor.deathNotification
        tested.liveMonitor( onOutput = monitor.onOutput, onProcessEnd = monitor.onDeath, cleanup = True )
        assert self.processAlive( 'closer' )
        assert self.processAlive( tag )
        LET_PROCESS_DIE_NATURALLY = 7
        time.sleep( LET_PROCESS_DIE_NATURALLY )
        assert not self.processAlive( tag )
        assert not self.processAlive( 'closer' )
        assert monitor.output == [ '{}_{}'.format( tag, i ) for i in ( 1, 2, 3, 4, 5 ) ]
        assert monitor.exitCode == 0
        assert monitor.deathNotification

    def test_live_monitoring_and_deliberate_killing_of_remote_process( self, closerCommand ):
        tag = str( random.random() )
        tested = closer.remote.Remote( USER, IP, "bash -c 'for i in 1 2 3 4 5 6 7 8 9 10; do echo {}_$i; sleep 1; done'".format( tag ), shell = True )
        tested.setCloserCommand( closerCommand )
        monitor = Monitor()
        tested.liveMonitor( onOutput = monitor.onOutput, onProcessEnd = monitor.onDeath, cleanup = True )
        assert not monitor.deathNotification
        assert self.processAlive( 'closer' )
        assert self.processAlive( tag )
        LET_PROCESS_LIVE_A_LITTLE = 3
        time.sleep( LET_PROCESS_LIVE_A_LITTLE )
        tested.terminate()
        SLACK = 1
        time.sleep( SLACK )
        assert not self.processAlive( tag )
        assert not self.processAlive( 'closer' )
        assert len( monitor.output ) > 0
        for index, line in enumerate( monitor.output ):
            assert line == '{}_{}'.format( tag, index + 1 )
        assert monitor.exitCode != 0
        assert monitor.deathNotification

    def test_live_monitoring_only_output( self, closerCommand ):
        tag = str( random.random() )
        tested = closer.remote.Remote( USER, IP, "bash -c 'for i in 1 2 3 4 5 6 7 8 9 10; do echo {}_$i; sleep 1; done'".format( tag ), shell = True )
        tested.setCloserCommand( closerCommand )
        monitor = Monitor()
        tested.liveMonitor( onOutput = monitor.onOutput, cleanup = True )
        assert not monitor.deathNotification
        assert self.processAlive( 'closer' )
        assert self.processAlive( tag )
        LET_PROCESS_LIVE_A_LITTLE = 3
        time.sleep( LET_PROCESS_LIVE_A_LITTLE )
        tested.terminate()
        SLACK = 1
        time.sleep( SLACK )
        assert not self.processAlive( tag )
        assert not self.processAlive( 'closer' )
        assert len( monitor.output ) > 0
        for index, line in enumerate( monitor.output ):
            assert line == '{}_{}'.format( tag, index + 1 )
        assert monitor.exitCode is None
        assert not monitor.deathNotification

    def processAlive( self, searchString, slack = 1 ):
        time.sleep( slack )
        searchString = str( searchString )
        completedProcess = subprocess.run( "ssh {}@{} pgrep -fl '{}'".format( USER, IP, searchString ), shell = True )
        return completedProcess.returncode == 0
