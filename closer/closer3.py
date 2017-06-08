import subprocess
import codecs
import threading
import signal
import argparse
import psutil
import os
import pickle
import sys
import pprint
import flask
import logging
killer = None
killedByUser = False

def killAll( * args ):
    global killer
    me = psutil.Process( os.getpid() )
    for process in me.children( recursive = True ):
        killMethod = getattr( process, killer )
        killMethod()

def quitWhenToldServer( port ):
    webApp = flask.Flask( 'closer' )

    @webApp.route("/kill")
    def kill():
        global killedByUser
        killedByUser = True
        killAll()
        shutdownFlask = flask.request.environ.get('werkzeug.server.shutdown')
        shutdownFlask()
        return 'bye'

    IMPOSSIBLE_LEVEL = 500
    log = logging.getLogger('werkzeug')
    log.setLevel( IMPOSSIBLE_LEVEL )
    webApp.logger.setLevel( IMPOSSIBLE_LEVEL )
    webApp.run( host = '0.0.0.0', port = port )

def interpret( hexedPickle ):
    pickled = codecs.decode( hexedPickle, 'hex' )
    return pickle.loads( pickled )

def main():
    global killedByUser
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
    signal.signal( signal.SIGTERM, killAll )
    if arguments.quitWhenTold:
        thread = threading.Thread( target = quitWhenToldServer, args = ( details[ 'port' ], ) )
        thread.daemon = True
        thread.start()
        exitCode = subProcess.wait()
        if killedByUser:
            thread.join()
        sys.exit( exitCode )
    else:
        exitCode = subProcess.wait()
        sys.exit( exitCode )

if __name__ == '__main__':
    main()
