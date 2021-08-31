#!/bin/bash -xe
[[ -d exported-artifacts ]] \
|| mkdir -p exported-artifacts

[[ -d tmp.repos ]] \
|| mkdir -p tmp.repos

# mock runner is not setting up the system correctly
# https://issues.redhat.com/browse/CPDEVOPS-242
dnf install -y $(cat automation/check-patch.packages)

autopoint
autoreconf -ivf
./configure
make dist
dnf builddep -y ovirt-vmconsole.spec
rpmbuild \
    -D "_topdir $PWD/tmp.repos" \
    -ta ovirt-vmconsole*.tar.gz

mv *.tar.gz exported-artifacts
find \
    "$PWD/tmp.repos" \
    -iname \*.rpm \
    -exec mv {} exported-artifacts/ \;
