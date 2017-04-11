# CLOSER

Closer was born because I had trouble with killing up processes I set up remotely via SSH.
That is, you want to run some SSH process in the background, and then you want to kill it, just 
like you would a local subprocess.

I couldn't find a good solution, so here's my take on it.

## Installation

You *must* install `closer` *both* on your local machine *and* the remote machine:

    $ pip install closer

## Caveats

* Again, `closer` must be installed on the remote machine for it to work.
* `closer` uses UDP packets for inter process communication. Firewalls make block `closer`. 

## Example Run

In this example we connect via SSH to a machien with IP `10.50.50.11` with a user called `vagrant`.
We run a `bash` shell that itself runs a `sleep`, not before echoing `whatup` to standard output.

After we quit the [`IPython`](http://ipython.org) process, the `Remote` object kills the remote process for us (becasue we specified `cleanup=True`.

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

the `onOutput` callback will be called for every line the remote process
produces on its standard output, and the `onProcessEnd` will be called when the
remote process exits.

## Python 3

Currently `closer` does not work with Python 3.
