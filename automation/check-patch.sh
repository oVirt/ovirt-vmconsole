#!/bin/bash -ex

automation/build-artifacts.sh

if [ -x /usr/bin/nosetests-3 ]
then
nosetests-3
elif [ -x /usr/bin/nosetests ]
then
nosetests
fi

