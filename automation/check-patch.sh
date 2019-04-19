#!/bin/bash -ex

automation/build-artifacts.sh

nosetests
