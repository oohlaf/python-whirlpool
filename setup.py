"""Whirlpool: Bindings for whirlpool hash reference implementation."""
from setuptools import setup, Extension

setup(
    version='1.1.2',
    ext_modules=[Extension('whirlpool', ['whirlpool/pywhirlpool.c'], include_dirs=['lib'])],
    data_files=[('whirlpool', ['lib/nessie.h', 'lib/Whirlpool.c'])],
    test_suite='test',
)
