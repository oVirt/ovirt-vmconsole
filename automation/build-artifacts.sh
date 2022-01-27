#!/bin/bash -xe

[[ -z "$EXPORT_DIR" ]] || \
EXPORT_DIR="exported-artifacts"

[[ -d "$EXPORT_DIR" ]] \
|| mkdir -p "$EXPORT_DIR"

[[ -d tmp.repos ]] \
|| mkdir -p tmp.repos

SUFFIX=".$(date -u +%Y%m%d%H%M%S).git$(git rev-parse --short HEAD)"

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
    -D "release_suffix ${SUFFIX}" \
    -ta ovirt-vmconsole*.tar.gz

mv *.tar.gz "$EXPORT_DIR"
find \
    "$PWD/tmp.repos" \
    -iname \*.rpm \
    -exec mv {} "$EXPORT_DIR"/ \;
