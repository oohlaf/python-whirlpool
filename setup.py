from distutils.core import setup, Extension

setup(name = "Whirlpool",
    version = "0.1",
    ext_modules = [Extension("whirlpool", ["main.c"])])

