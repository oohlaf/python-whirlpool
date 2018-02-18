# python-whirlpool

[![Travis CI Build Status](https://travis-ci.org/oohlaf/python-whirlpool.svg?branch=master)](https://travis-ci.org/oohlaf/python-whirlpool)
[![AppVeyor Build Status](https://ci.appveyor.com/api/projects/status/pw35grm8ald8lg22/branch/master?svg=true)](https://ci.appveyor.com/project/oohlaf/python-whirlpool/branch/master)
[![License: Unlicense](https://img.shields.io/badge/license-Unlicense-blue.svg)](http://unlicense.org/)

The [Whirlpool] algorithm is designed by Vincent Rijmen and Paulo S.L.M. Barreto.
It is a secure and modern digest function that has been recommended by the
[NESSIE] project and adopted in the ISO/IEC 10118-3 international standard.

Digest functions, also known as hash functions, produce fixed-length output (a
digest or hash) from a variable-length message. They are designed to be a
one-way function.

This library is a Python wrapper around the Whirlpool C reference implementation.
The Whirlpool reference implementations are public domain, as is this code.

The first version of the wrapper was written by James Cleveland with help
from #python on irc.freenode.net.

Later on the wrapper was rewritten by Olaf Conradi to use the hashlib interface
and he made the library compatible with Python 3.

## Installation

This library is available on [PyPI].

    pip install whirlpool

## Usage

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

## Development

The source code is available on [GitHub].

    git clone https://github.com/oohlaf/python-whirlpool.git
    cd python-whirlpool

Install in development mode using:

    python setup.py develop

Or install in editable mode using pip:

    pip install -e .

## Testing

This module is tested using Python 2.7, PyPy, and Python 3.3 and up.

You can run the test suite using

    python setup.py test

[Whirlpool]: https://en.wikipedia.org/wiki/Whirlpool_(cryptography)
[NESSIE]: https://www.cosic.esat.kuleuven.be/nessie/
[PyPI]: https://pypi.python.org/pypi/Whirlpool
[GitHub]: https://github.com/oohlaf/python-whirlpool
