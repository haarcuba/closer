# CLOSER

Closer was born because I had trouble with killing up processes I set up remotely via SSH.
That is, you want to run some SSH process in the background, and then you want to kill it, just 
like you would a local subprocess.

I couldn't find a good solution, so here's my take on it.

Closer has evolved to do more than just automatic remote process cleanup.
Here are the main features:

* kill the remote process (either by choice, or automatically at the end of the calling process)
* capture the remote process's output
* live monitoring of remote process output
* get a callback upon remote process' death

## License

Do whatever you want with closer, but be kind enough to share your improvements with a pull request.

## Installation

You *must* install `closer` *both* on your local machine *and* the remote machine:

    $ pip install closer

## Caveats

* Again, `closer` must be installed on the remote machine for it to work.
* `closer` uses TCP communication with the remote process. Firewalls may block `closer`. 

## Example Run

In this example we connect via SSH to a machine with IP `10.50.50.11` with a user called `vagrant`.
We run a `bash` shell that itself runs a `sleep`, not before echoing `whatup` to standard output.

After we quit the [`IPython`](http://ipython.org) process, the `Remote` object kills the remote process for us (because we specified `cleanup=True`.

```python
$ ipython
Python 2.7.12+ (default, Sep 17 2016, 12:08:02) 
Type "copyright", "credits" or "license" for more information.

IPython 5.1.0 -- An enhanced Interactive Python.
?         -> Introduction and overview of IPython's features.
%quickref -> Quick reference.
help      -> Python's own help system.
object?   -> Details about 'object', use 'object??' for extra details.

In [1]: import closer.remote

In [2]: r = closer.remote.Remote( 'vagrant', '10.50.50.11', [ 'bash', '-c', 'echo whatup; sleep 1500;' ] )

In [3]: r.background(cleanup=True) # launches remote process in the background

whatup
In [4]: quit()  # remote process dies automatically - check it out on your own remote server
```

## Explicitly Closing All Remote Background (with `cleanup=True`) Processes and Handling `SIGTERM`

`closer` relies on [`atexit`](https://docs.python.org/2.7/library/atexit.html)
If your process dies as a result of receiving `SIGTERM`, the `atexit` handler will not run.

`closer` provides a solution by allowing you to explicitly close all `Remote` processes:

```python
    closer.remote.Remote.tidyUp()
```

NOTE: `tidyUp()` will ONLY WORK for `Remote` objects that run with
`.background(cleanup=True)`. If you did not specify `cleanup=True` it is false
by default.

To handle `SIGTERM`, e.g.:


```python
import closer.remote
import signal
import sys

def handleSIGTERM( * args ):
    closer.remote.Remote.tidyUp()
    sys.exit( 1 )

signal.signal( signal.SIGTERM, handleSIGTERM )
```

## My Remote Machine's `closer` Script is Not in the System PATH

Use the `.setCloserCommand()`, e.g.

```python
remoteObject = closer.remote.Remote( ... )
remoteObject.setCloserCommand( '/path/to/closer' )
```

## I want to specify a different SSH port or other options

Here you go:

```python
remoteObject.sshPort = SOME_OTHER_PORT
remoteObject.sshOptions( 'StrictHostKeyChecking=no' ) # this goes into the -o ssh flag
```

## Other Perks

The `Remote` class also allows you to run processes synchronously, i.e. the following [IPython](http://ipython.org) session:

```python
In [7]: r = closer.remote.Remote( 'vagrant', '10.50.50.11', [ 'ls', '-ltr', '/var' ] )

In [8]: r.foreground()
total 44
drwxrwsr-x  2 root staff  4096 Apr 10  2014 local
drwxr-xr-x  2 root root   4096 Apr 10  2014 backups
drwxr-xr-x  2 root root   4096 Feb  8 20:41 opt
drwxrwsr-x  2 root mail   4096 Feb  8 20:41 mail
lrwxrwxrwx  1 root root      4 Feb  8 20:41 run -> /run
lrwxrwxrwx  1 root root      9 Feb  8 20:41 lock -> /run/lock
drwxr-xr-x  5 root root   4096 Feb  8 20:42 spool
drwxrwxrwt  2 root root   4096 Feb  8 20:43 crash
drwxr-xr-x 11 root root   4096 Feb  8 21:35 cache
drwxr-xr-x 47 root root   4096 Feb  8 21:36 lib
drwxr-xr-x  3 root root   4096 Feb 12 20:22 chef
drwxrwxrwt  2 root root   4096 Feb 12 22:11 tmp
drwxrwxr-x 10 root syslog 4096 Feb 13 18:49 log
```

And you can capture the output if you like:


```python
In [6]: r = closer.remote.Remote( 'vagrant', '10.50.50.11', [ 'ls', '-ltr', '/var' ] )

In [7]: text = r.output()

In [8]: text.split('\n')
Out[8]: 
['total 44',
 'drwxrwsr-x  2 root staff  4096 Apr 10  2014 local',
 'drwxr-xr-x  2 root root   4096 Apr 10  2014 backups',
 'drwxr-xr-x  2 root root   4096 Feb  8 20:41 opt',
 'drwxrwsr-x  2 root mail   4096 Feb  8 20:41 mail',
 'lrwxrwxrwx  1 root root      4 Feb  8 20:41 run -> /run',
 'lrwxrwxrwx  1 root root      9 Feb  8 20:41 lock -> /run/lock',
 'drwxr-xr-x  5 root root   4096 Feb  8 20:42 spool',
 'drwxrwxrwt  2 root root   4096 Feb  8 20:43 crash',
 'drwxr-xr-x 11 root root   4096 Feb  8 21:35 cache',
 'drwxr-xr-x 47 root root   4096 Feb  8 21:36 lib',
 'drwxr-xr-x  3 root root   4096 Feb 12 20:22 chef',
 'drwxrwxrwt  2 root root   4096 Feb 12 22:11 tmp',
 'drwxrwxr-x 10 root syslog 4096 Feb 13 18:49 log',
 '']
```

By default `.foreground()` will raise an exception if the process fails. You can disable this behaviour with `.foreground( check = False )`.

## Timeout on Remote Processes

You can impose a timeout on the time it takes the remote process to end

```python
remote = closer.remote.Remote( 'myUser', 'myHost', [ 'bash', '-c', 'echo hiThere; sleep 10;' ] )
remote.run( timeout = 3 )
```

Since we sleep here 10 seconds, the timeout will go off, and `run` will raise an exception:

    RemoteProcessTimeout: runtime exceeded 3 seconds for remote process: {'args': (['bash', '-c', 'echo hiThere; sleep 10;'],), 'kwargs': {}}


## Live Monitoring of Remote Process Output and Death

You can monitor a remote processes' output and death events using the `liveMonitor` method. Try this:

```python
def onOutput( line ):
    print "got: {}".format( line )

def onProcessEnd( exitCode ):
    print "process died with exitCode={}".format( exitCode )

tested = closer.remote.Remote( 'my-user', 'my-host', "bash -c 'for i in 1 2 3 4 5 6 7 8 9 10; do echo $i; sleep 1; done; exit 7'", shell = True )
tested.liveMonitor( onOutput = onOutput, onProcessEnd = onProcessEnd, cleanup = True )
LET_PROCESS_DIE_NATURALLY = 12
time.sleep( LET_PROCESS_DIE_NATURALLY )
```

The `onOutput` callback will be called for every line the remote process
produces on its standard output, and the `onProcessEnd` will be called when the
remote process exits.

## Python 3

`closer` works with Python 3 just fine, but there is a caveat. Assuming that the local host has the Python 3 `closer` installed:

* if the remote host has a Python 3 based closer - no problem
* if the remote host has a Python 2 based closer, you must set the closer command like so:


```python
remoteObject.setCloserCommand( '/path/to/closer' ) 
```
    
Otherwise, it will look for a local `closer3` script and will not find one.

**PYTHON 2 SUPPORT WILL BE DROPPED EVENTUALLY**
