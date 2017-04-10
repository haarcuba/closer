import time
import closer.remote
import subprocess
import random

IP = '10.50.50.11'
USER = 'vagrant'

class TestRealLiveProcesses( object ):
    def test_run_ls_in_vagrant_via_ssh( self ):
        tested = closer.remote.Remote( USER, IP, "bash -c 'exit 77'", shell = True )
        exitCode = tested.foreground( check = False )
        assert exitCode == 77

    def test_kill_a_remote_closer_process( self ):
        seconds = str( random.randint( 1000, 2000 ) )
        tested = closer.remote.Remote( USER, IP, [ "sleep", seconds ] )
        tested.background( cleanup = False )
        assert self.processAlive( 'closer' )
        tested.terminate()
        assert not self.processAlive( 'closer' )

    def test_remote_subprocess_dies_with_closer_process( self ):
        tag = str( random.random() )
        tested = closer.remote.Remote( USER, IP, "bash -c 'sleep 1000; echo tag={}'".format( tag ), shell = True )
        tested.background( cleanup = False )
        assert self.processAlive( 'closer' )
        assert self.processAlive( 'tag={}'.format( tag ) )
        tested.terminate()
        assert not self.processAlive( 'closer' )
        assert not self.processAlive( 'tag={}'.format( tag ) )

    def processAlive( self, searchString ):
        searchString = str( searchString )
        exitCode = subprocess.call( "ssh {}@{} pgrep -fl '{}'".format( USER, IP, searchString ), shell = True )
        return exitCode == 0

    @classmethod
    def teardown_class( cls ):
        subprocess.call( "ssh {}@{} pkill -f closer".format( USER, IP ), shell = True )
