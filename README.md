python-whirlpool
================

This is just a wrapper to the Whirlpool C reference implementation. 
The Whirlpool reference implementations are public domain, as is this code.

Wrapper written by James Cleveland with help from #python on irc.freenode.net.

Wrapper modified by Olaf Conradi to use the hashlib interface.

Usage
-----

This is the same interface as provided by the other digest algorithms in
Python's hashlib.
    
    import whirlpool

    wp = whirlpool.new("My String")
    hashed_string = wp.hexdigest()

    wp.update("My Salt")
    hashed_string = wp.hexdigest()

Deprecated usage
----------------

For backward compatibility the old interface remains available.

    import whirlpool

    hashed_string = whirlpool.hash("My String")

