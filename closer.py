import subprocess
import time
import signal
import argparse
import psutil
import os
import cPickle
import sys

def killAllDecendants( * args ):
    me = psutil.Process( os.getpid() )
    for process in me.children( recursive = True ):
        process.terminate()

    quit()

def interpret( hexedPickle ):
    pickled = hexedPickle.decode( 'hex' )
    return cPickle.loads( pickled )

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument( 'popenArgsKwargsInHexedPickle' )
    arguments = parser.parse_args()

    script = interpret( arguments.popenArgsKwargsInHexedPickle )

    sys.stdout.write( '{}\n'.format( os.getpid() ) )
    sys.stdout.flush()
    subprocess.Popen( * script[ 'args' ], ** script[ 'kwargs' ] )
    signal.signal( signal.SIGTERM, killAllDecendants )
    signal.signal( signal.SIGINT, killAllDecendants )
    while True:
        time.sleep( 1000 )

if __name__ == '__main__':
    main()
