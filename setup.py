""" Whirpool: Bindings for whirlpool hash reference implementation.

The Whirlpool hashing algorithm (http://www.larc.usp.br/~pbarreto/WhirlpoolPage.html),
written by Vincent Rijmen and Paulo S. L. M. Barreto is a secure, modern hash which is
as yet unbroken and fairly obscure. Provided on the algorithm's page is a C reference
implementation which is fairly simple to wrap with a Python extension, which is much
faster than re-implementation in pure Python.
"""
from setuptools import setup, Extension


doclines = __doc__.split("\n")

setup(name = "Whirlpool",
    version = "0.3",
    description = doclines[0],
    long_description = "\n".join(doclines[2:]),
    url = "https://github.com/radiosilence/python-whirlpool",
    maintainer = "James E. Cleveland",
    maintainer_email = "jamescleveland@gmail.com",
    license = "Public Domain",
    platforms = ["any"],
    ext_modules = [Extension("whirlpool", ["main.c"])],
    data_files = [("whirlpool", ['nessie.h', "Whirlpool.c"])],
    test_suite = "tests"
)

