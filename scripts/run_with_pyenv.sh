#!/usr/bin/env bash
set -euo pipefail

if ! command -v pyenv >/dev/null 2>&1; then
  echo "pyenv is not installed. Install it first: https://github.com/pyenv/pyenv" >&2
  exit 1
fi

version="${1:-3.13}"

if [[ "$version" == "2.7" ]]; then
  version="2.7.18"
fi

if ! pyenv versions --bare | grep -Fxq "$version"; then
  echo "Python $version is not installed under pyenv yet. Install it first, for example: pyenv install $version" >&2
  exit 1
fi

pyenv local "$version"
python -m pip install --upgrade pip setuptools wheel
python -m pip install .
python -m unittest discover -s test -p 'test_*.py'
