#!/bin/bash

pip-compile dev-requirements.in
pip install --upgrade -r dev-requirements.txt
pre-commit install
flake8
