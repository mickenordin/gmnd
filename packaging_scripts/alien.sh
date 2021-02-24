#!/usr/bin/env bash
# This is where I keep my sources
BASEDIR=~/sources
# Version of gmnd
VERSION=$(awk '/.*SERVER_SOFTWARE/ {print $4}' ${BASEDIR}/gmnd/gmnd/__init__.py|sed "s/'//" )

cd ${BASEDIR}

# Import signing key
sudo rpm --import ${BASEDIR}/repo/PUBLIC.KEY 

# Convert deb to rpm
sudo alien --scripts -g -r ${BASEDIR}/gmnd_${VERSION}_all.deb

# Remove generated specfile
sudo rm ${BASEDIR}/gmnd-${VERSION}/gmnd-*.spec

# Replace with our own
sed "s/##VERSION##/${VERSION}/" ${BASEDIR}/gmnd/rpm/gmnd-TEMPLATE.spec | sudo tee ${BASEDIR}/gmnd-${VERSION}/gmnd-${VERSION}.spec

# Change to build dir
cd gmnd-${VERSION}

# Build rpm and put in repo
cp ${BASEDIR}/gmnd/rpm/macros ~/.rpmmacros
sudo rpmbuild --buildroot=$(pwd) -bb gmnd-${VERSION}.spec
sudo chown ${USER}:${USER} ${BASEDIR}/gmnd-${VERSION}.noarch.rpm 
rpm --addsign ${BASEDIR}/gmnd-${VERSION}.noarch.rpm
cp ${BASEDIR}/gmnd-${VERSION}.noarch.rpm ${BASEDIR}/repo/rpm/
createrepo_c ${BASEDIR}/repo/rpm/
