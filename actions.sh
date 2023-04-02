#!/bin/bash

# Simple directives for building subsequent
# python packages.

set -eu -o pipefail

# Builds package distributable.
build() {
    python setup.py sdist bdist_wheel
}

# Install package in local virtual environment.
local() {
    find dist/ -type f -iname "*.whl" | xargs python -m pip install --force-reinstall
}

publish() {
    python -m twine upload dist/*
}

for command in "$@"
do
    $command
done
