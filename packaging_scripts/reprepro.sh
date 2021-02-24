#!/usr/bin/env bash
# Where I keep the sources
BASEDIR=~/sources
# Version of gmnd
VERSION=$(awk '/.*SERVER_SOFTWARE/ {print $4}' ${BASEDIR}/gmnd/gmnd/__init__.py|sed "s/'//" )

# Change to source dir
cd ${BASEDIR}/gmnd

# Build deb
dpkg-buildpackage -us -uc

# Add binary and source to repo
reprepro --basedir ${BASEDIR}/repo/debian includedeb unstable ${BASEDIR}/gmnd_${VERSION}_all.deb
reprepro --basedir ${BASEDIR}/repo/debian -S net --priority optional includedsc unstable ${BASEDIR}/gmnd_${VERSION}.dsc
