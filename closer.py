import subprocess
import time
import signal
import argparse
import psutil
import os
import cPickle
import sys
import logging
logging.basicConfig( level = logging.INFO )

def killAllAndQuit( * args ):
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
    parser.add_argument( '--quit-on-input', dest='quitOnInput', action='store_true' )
    arguments = parser.parse_args()

    popenDetails = interpret( arguments.popenArgsKwargsInHexedPickle )
    logging.info( 'will run Popen with: args={args} kwargs={kwargs}'.format( ** popenDetails ) )
    subprocess.Popen( * popenDetails[ 'args' ], ** popenDetails[ 'kwargs' ] )
    signal.signal( signal.SIGTERM, killAllAndQuit )
    if arguments.quitOnInput:
        raw_input()
        killAllAndQuit()
    else:
        while True:
            time.sleep( 1000 )

if __name__ == '__main__':
    main()
