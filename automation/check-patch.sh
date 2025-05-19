#!/bin/bash -ex

automation/build-artifacts.sh

cd src/
python3 -m unittest discover ../tests "*_test.py"