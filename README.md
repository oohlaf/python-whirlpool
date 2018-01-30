python-whirlpool
================

The Whirlpool algorithm is designed by Vincent Rijmen and Paulo S.L.M. Barreto.
This is just a wrapper to the Whirlpool C reference implementation. 
The Whirlpool reference implementations are public domain, as is this code.

Wrapper written by James Cleveland with help from #python on irc.freenode.net.

Wrapper extended to use the hashlib interface and ported to Python 3 by
Olaf Conradi.

Usage
-----

This is the same interface as provided by the other digest algorithms in
Python's hashlib.
    
    import whirlpool

    wp = whirlpool.new("My String")
    hashed_string = wp.hexdigest()

    wp.update("My Salt")
    hashed_string = wp.hexdigest()

Starting with Python 3 text strings (as shown above) are stored as unicode.
You need to specify the encoding of these strings before hashing.

    wp = whirlpool.new(data.encoding('utf-8'))

Strings that are marked as binary do not need encoding.

Testing
-------

This module is tested using Python 2.7 and Python 3.3.
