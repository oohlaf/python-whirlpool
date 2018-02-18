"""Whirlpool: Bindings for whirlpool hash reference implementation."""
import os
import sys

from setuptools import setup, Extension

if sys.version_info.major < 3:
    from io import open


VERSION = '1.0.0'
GITHUB_URL = 'https://github.com/oohlaf/python-whirlpool'
DOWNLOAD_URL = '{}/archive/{}.zip'.format(GITHUB_URL, VERSION)

DOCLINES = __doc__.strip().split('\n')

HERE = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(HERE, 'README.md'), encoding='utf-8') as f:
    README = '\n' + f.read()
with open(os.path.join(HERE, 'CHANGELOG.md'), encoding='utf-8') as f:
    CHANGELOG = '\n' + f.read()
LONG_DESC = README + '\n' + CHANGELOG


try:
    import pypandoc
    LONG_DESC = pypandoc.convert_text(LONG_DESC, 'rst', format='markdown')
    LONG_DESC_CTYPE = 'text/x-rst'
except (IOError, ImportError):
    LONG_DESC_CTYPE = 'text/markdown'


setup(name="Whirlpool",
      version=VERSION,
      description=DOCLINES[0],
      long_description=LONG_DESC,
      long_description_content_type=LONG_DESC_CTYPE,
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
          "Programming Language :: Python :: Implementation :: CPython",
          "Programming Language :: Python :: Implementation :: PyPy",
          "Topic :: Security :: Cryptography",
          "Topic :: Software Development :: Libraries :: Python Modules",
          ],
      keywords="digest hashlib whirlpool",
      url=GITHUB_URL,
      download_url=DOWNLOAD_URL,
      maintainer="Olaf Conradi",
      maintainer_email="olaf@conradi.org",
      license="Public Domain",
      python_requires=">=2.7,!=3.0.*,!=3.1.*,!=3.2.*",
      platforms=["any"],
      ext_modules=[Extension("whirlpool", ["whirlpool/pywhirlpool.c"],
                             include_dirs=["lib"])],
      data_files=[("whirlpool", ['lib/nessie.h', "lib/Whirlpool.c"])],
      test_suite="test"
     )
