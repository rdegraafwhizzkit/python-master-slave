#!/bin/bash

chmod 755 destroy_venv.sh
./destroy_venv.sh

PYTHON=python3.11
which ${PYTHON} > /dev/null 2>&1 || PYTHON=python3

${PYTHON} -m venv .venv
. .venv/bin/activate
pip install --upgrade pip pip-tools

pip-compile requirements.in
pip install --upgrade -r requirements.txt
