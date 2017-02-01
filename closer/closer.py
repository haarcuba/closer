import subprocess
import time
import signal
import argparse
import psutil
import os
import cPickle
import sys

killer = None

def killAllAndQuit( * args ):
    global killer
    me = psutil.Process( os.getpid() )
    for process in me.children( recursive = True ):
        killMethod = getattr( process, killer )
        killMethod()

    quit()

def interpret( hexedPickle ):
    pickled = hexedPickle.decode( 'hex' )
    return cPickle.loads( pickled )

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument( 'popenArgsKwargsInHexedPickle' )
    parser.add_argument( '--killer', choices = [ 'kill', 'terminate' ], default = 'terminate' )
    parser.add_argument( '--quit-on-input', dest='quitOnInput', action='store_true' )
    arguments = parser.parse_args()
    global killer
    killer = arguments.killer

    popenDetails = interpret( arguments.popenArgsKwargsInHexedPickle )
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
