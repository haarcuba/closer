import closer.remote
import time

def onOutput( line ):
    print "got: {}".format( line )

def onProcessEnd( exitCode ):
    print "process died with exitCode={}".format( exitCode )

USER = 'vagrant'
IP = '10.50.50.11'
tested = closer.remote.Remote( USER, IP, "bash -c 'for i in 1 2 3 4 5 6 7 8 9 10; do echo $i; sleep 1; done; exit 7'", shell = True )
tested.liveMonitor( onOutput = onOutput, onProcessEnd = onProcessEnd, cleanup = True )
LET_PROCESS_DIE_NATURALLY = 12
time.sleep( LET_PROCESS_DIE_NATURALLY )
