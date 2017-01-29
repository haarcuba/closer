import subprocess
import cPickle

def remote( user, host, ownKwargs, * popenArgs, ** popenKwargs ):
    closer = dict( args = popenArgs, kwargs = popenKwargs )
    hexedPickle = cPickle.dumps( closer ).encode( 'hex' )
    sshCommand = [ 'ssh', '{}@{}'.format( user, host ), 'closer', '--quit-on-input', hexedPickle ]
    return subprocess.Popen( sshCommand, stdin = subprocess.PIPE, ** ownKwargs )
