#!/usr/bin/env bash
BASEDIR=~/sources
${BASEDIR}/gmnd/packaging_scripts/version.sh
${BASEDIR}/gmnd/packaging_scripts/reprepro.sh
${BASEDIR}/gmnd/packaging_scripts/alien.sh
