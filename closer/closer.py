import subprocess
import socket
import signal
import argparse
import psutil
import os
import pickle
import sys
import pprint

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
    return pickle.loads( pickled )

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument( 'detailsHexedPickle' )
    parser.add_argument( '--killer', choices = [ 'kill', 'terminate' ], default = 'terminate' )
    parser.add_argument( '--quit-when-told', dest='quitWhenTold', action='store_true' )
    parser.add_argument( '--interpret', action='store_true' )
    arguments = parser.parse_args()
    global killer
    killer = arguments.killer

    details = interpret( arguments.detailsHexedPickle )
    if arguments.interpret:
        pprint.pprint( details )
        return

    popenDetails = details[ 'popenDetails' ]
    subProcess = subprocess.Popen( * popenDetails[ 'args' ], ** popenDetails[ 'kwargs' ] )
    signal.signal( signal.SIGTERM, killAllAndQuit )
    if arguments.quitWhenTold:
        sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
        sock.connect( details[ 'peer' ] )
        sock.send( 'hi' )
        sock.recv( 1024 )
        killAllAndQuit()
    else:
        sys.exit( subProcess.wait() )

if __name__ == '__main__':
    main()
