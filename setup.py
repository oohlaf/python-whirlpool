"""Whirlpool: Bindings for whirlpool hash reference implementation."""
import os
import sys

from setuptools import setup, Extension

if sys.version_info.major < 3:
    from io import open


doclines = __doc__.strip().split('\n')


HERE = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(HERE, 'README.md'), encoding='utf-8') as f:
    README = '\n' + f.read()
with open(os.path.join(HERE, 'CHANGELOG.md'), encoding='utf-8') as f:
    CHANGELOG = '\n' + f.read()


setup(name = "Whirlpool",
    version = "1.0.0.dev1",
    description = doclines[0],
    long_description = README + '\n' + CHANGELOG,
    long_description_content_type = "text/markdown",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: Public Domain",
        "Programming Language :: C",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Security :: Cryptography",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
    url = "https://github.com/oohlaf/python-whirlpool",
    maintainer = "Olaf Conradi",
    maintainer_email = "olaf@conradi.org",
    license = "Public Domain",
    platforms = ["any"],
    ext_modules = [Extension("whirlpool", ["whirlpool/pywhirlpool.c"],
                             include_dirs=["lib"])],
    data_files = [("whirlpool", ['lib/nessie.h', "lib/Whirlpool.c"])],
    test_suite = "test"
)
