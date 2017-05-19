import time
import closer.remote
import subprocess
import random

IP = '10.50.50.11'
USER = 'vagrant'

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

    def test_run_ls_in_vagrant_via_ssh( self ):
        tested = closer.remote.Remote( USER, IP, "bash -c 'exit 77'", shell = True )
        exitCode = tested.foreground( check = False )
        assert exitCode == 77

    def test_remote_subprocess_dies_when_closer_told_to_quit( self ):
        tag = str( random.random() )
        tested = closer.remote.Remote( USER, IP, "bash -c 'sleep 1000; echo tag={}'".format( tag ), shell = True )
        tested.background( cleanup = False )
        assert self.processAlive( 'closer' )
        assert self.processAlive( 'tag={}'.format( tag ), slack = 0 )
        tested.terminate()
        assert not self.processAlive( 'tag={}'.format( tag ), slack = 0 )
        assert not self.processAlive( 'closer' )

    def test_closer_process_dies_if_remote_subprocess_dies( self ):
        tag = str( random.random() )
        tested = closer.remote.Remote( USER, IP, "bash -c 'sleep 3; echo tag={}'".format( tag ), shell = True )
        tested.background( cleanup = False )
        assert self.processAlive( 'closer' )
        assert self.processAlive( 'tag={}'.format( tag ) )
        LET_PROCESS_DIE_NATURALLY = 2
        time.sleep( LET_PROCESS_DIE_NATURALLY )
        assert not self.processAlive( 'tag={}'.format( tag ) )
        assert not self.processAlive( 'closer' )

    def test_live_monitoring_of_remote_process( self ):
        tag = str( random.random() )
        tested = closer.remote.Remote( USER, IP, "bash -c 'for i in 1 2 3 4 5; do echo {}_$i; sleep 1; done'".format( tag ), shell = True )
        monitor = Monitor()
        tested.liveMonitor( onOutput = monitor.onOutput, onProcessEnd = monitor.onDeath, cleanup = True )
        assert self.processAlive( 'closer' )
        assert self.processAlive( tag )
        LET_PROCESS_DIE_NATURALLY = 7
        time.sleep( LET_PROCESS_DIE_NATURALLY )
        assert not self.processAlive( tag )
        assert not self.processAlive( 'closer' )
        assert monitor.output == [ '{}_{}'.format( tag, i ) for i in ( 1, 2, 3, 4, 5 ) ]
        assert monitor.exitCode == 0

    def test_live_monitoring_and_deliberate_killing_of_remote_process( self ):
        tag = str( random.random() )
        tested = closer.remote.Remote( USER, IP, "bash -c 'for i in 1 2 3 4 5 6 7 8 9 10; do echo {}_$i; sleep 1; done'".format( tag ), shell = True )
        monitor = Monitor()
        tested.liveMonitor( onOutput = monitor.onOutput, onProcessEnd = monitor.onDeath, cleanup = True )
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

    def test_live_monitoring_only_output( self ):
        tag = str( random.random() )
        tested = closer.remote.Remote( USER, IP, "bash -c 'for i in 1 2 3 4 5 6 7 8 9 10; do echo {}_$i; sleep 1; done'".format( tag ), shell = True )
        monitor = Monitor()
        tested.liveMonitor( onOutput = monitor.onOutput, cleanup = True )
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
        exitCode = subprocess.call( "ssh {}@{} pgrep -fl '{}'".format( USER, IP, searchString ), shell = True )
        return exitCode == 0
