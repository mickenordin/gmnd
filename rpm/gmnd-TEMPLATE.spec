Buildroot: /home/micke/sources/gmnd-##VERSION##
Name: gmnd
Version: ##VERSION##
Release: 1
Requires: python3-yaml
Summary: gMNd is a gemini server written in python 
License: AGPLv3+ 
Distribution: Fedora

%define _binary_filedigest_algorithm 2
%define _rpmdir ../
%define _rpmfilename %%{NAME}-%%{VERSION}.noarch.rpm
%define _unpackaged_files_terminate_build 0

%description
gMNd is a gemini server written in python. It has support for serving
static files, or run cgi-scripts. Documentation will primarily be supplied
via gemini://mic.ke/gmnd/docs

%files
%docdir /usr/share/doc/gmnd
"/usr/share/doc/gmnd/changelog.gz"
"/usr/share/doc/gmnd/copyright"
%config "/etc/gmnd/config.yml"
%dir "/usr/lib/python3/dist-packages/gmnd/"
"/usr/lib/python3/dist-packages/gmnd/__init__.py"
