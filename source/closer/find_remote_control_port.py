import requests
import threading
import logging
from closer import closer3
import time

class FindRemoteControlPort:
    def __init__( self, remote ):
        self._remote = remote
        thread = threading.Thread( target = self._go )
        thread.daemon = True
        thread.start()

    def _go( self ):
        SLACK_FOR_FLASK_TO_START = 2
        time.sleep( SLACK_FOR_FLASK_TO_START )
        for port in closer3.spreadAround( self._remote.controlPort, 10 ):
            if self._pingRemote( port ):
                logging.info( 'remote closer listening on {}:{}'.format( self._remote.host, port ) )
                self._remote.controlPort = port

            time.sleep( 1 )

        logging.error( 'remote closer not found' )

    def _pingRemote( self, port ):
        url = 'http://{}:{}/ping'.format( self._remote.host, port )
        try:
            response = requests.get( url )
            if response.status_code == 200 and response.text == self._remote.uuid:
                return True
        except requests.exceptions.RequestException as e:
            logging.info( 'while pinging {}'.format( e ) )

        return False

