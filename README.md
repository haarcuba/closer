# Closer

Closer was born because I had trouble with killing up processes I set up remotely via SSH.
That is, you want to run some SSH process in the background, and then you want to kill it, just 
like you would a local subprocess.

I couldn't find a good solution, so here's my take on it.

## Installation

You *must* install `closer` *both* on your local machine *and* the remote machine:

    $ pip install closer

## Example Run

In this example we connect via SSH to a machien with IP `10.50.50.11` with a user called `vagrant`.
We run a `bash` shell that itself runs a `sleep`, not before echoing `whatup` to standard output.

After we quit the `IPython` process, the `Remote` object kills the remote process for us (becasue we specified `cleanup=True`.

```ipython
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

In [3]: r.background(cleanup=True)

whatup
In [4]: quit()
```
