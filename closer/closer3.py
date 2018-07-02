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

def spreadAround( middle, delta ):
    yield middle
    for i in range( 1, delta + 1 ):
        yield middle + i
        yield middle - i

def _launchWebApp( webApp, host, port ):
    for port_ in spreadAround( port, 10 ):
        try:
            return webApp.run( host = '0.0.0.0', port = port_ )
        except OSError as e:
            PORT_TAKEN = 98
            if e.errno != PORT_TAKEN:
                raise

def quitWhenToldServer( port, uuid ):
    webApp = flask.Flask( 'closer' )

    @webApp.route("/kill")
    def kill():
        global killedByUser
        killedByUser = True
        killAll()
        shutdownFlask = flask.request.environ.get('werkzeug.server.shutdown')
        shutdownFlask()
        return 'bye'

    @webApp.route("/ping")
    def ping():
        return uuid

    IMPOSSIBLE_LEVEL = 500
    log = logging.getLogger('werkzeug')
    log.setLevel( IMPOSSIBLE_LEVEL )
    webApp.logger.setLevel( IMPOSSIBLE_LEVEL )
    _launchWebApp( webApp, '0.0.0.0', port )

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
        thread = threading.Thread( target = quitWhenToldServer, args = ( details[ 'port' ], details[ 'uuid' ] ) )
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
