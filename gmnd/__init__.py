#!/usr/bin/python3
import logging
import mimetypes
import os
import re
import socket
import ssl
import subprocess
import sys
from socket import AF_INET, SHUT_RDWR, SO_REUSEADDR, SOCK_STREAM, SOL_SOCKET
from urllib.parse import urlparse

import yaml


class gMNd:
    def __init__(self, options={}):
        self.allow_dir_list = options.get('allow_dir_list', False)
        self.base_path = options.get('base_path', './content')
        self.cgi_registry = options.get('cgi_registry', None)
        self.config_file = options.get('config_file', None)
        self.listen_addr = options.get('listen_addr', '127.0.0.1')
        self.listen_port = options.get('listen_port', 1965)
        self.logg_level = options.get('logg_level', logging.INFO)
        self.server_cert = options.get('server_cert', './certs/cert.pem')
        self.server_key = options.get('server_key', './certs/cert.key')
        logging.basicConfig(stream=sys.stderr, level=self.logg_level)
        if self.config_file:
            if os.path.isfile(self.config_file):
                self.read_config()
                logging.basicConfig(stream=sys.stderr, level=self.logg_level)
            else:
                logging.warning("Config file supplied, but it is not a file")
        if not (os.path.isfile(self.server_cert)
                and os.path.isfile(self.server_key)):
            logging.error("ERROR: " + str(self.server_cert) + " and/or " +
                          str(self.server_key) +
                          " does not exist, and TLS is required for gemini.")
            sys.exit(1)
        self.bindsocket = socket.socket()

        self.bindsocket.bind((self.listen_addr, self.listen_port))
        self.bindsocket.listen(5)

    def read_config(self):
        with open(self.config_file) as configfile:
            config_dict = yaml.load(configfile, Loader=yaml.FullLoader)
            if 'allow_dir_list' in config_dict:
                self.allow_dir_list = config_dict['allow_dir_list']
            if 'base_path' in config_dict:
                self.base_path = config_dict['base_path']
            if 'cgi_registry' in config_dict:
                self.cgi_registry = config_dict['cgi_registry']
            if 'listen_addr' in config_dict:
                self.listen_addr = config_dict['listen_addr']
            if 'listen_port' in config_dict:
                self.listen_port = config_dict['listen_port']
            if 'logg_level' in config_dict:
                if config_dict['logg_level'] == "CRITICAL":
                    self.logg_level = logging.CRITICAL
                elif config_dict['logg_level'] == "DEBUG":
                    self.logg_level = logging.DEBUG
                elif config_dict['logg_level'] == "ERROR":
                    self.logg_level = logging.ERROR
                elif config_dict['logg_level'] == "INFO":
                    self.logg_level = logging.INFO
                elif config_dict['logg_level'] == "NOTSET":
                    self.logg_level = logging.NOTSET
                elif config_dict['logg_level'] == "WARNING":
                    self.logg_level = logging.WARNING
            if 'server_cert' in config_dict:
                self.server_cert = config_dict['server_cert']
            if 'server_key' in config_dict:
                self.server_key = config_dict['server_key']

    def run(self):
        while True:
            logging.debug("Waiting for client")
            newsocket, fromaddr = self.bindsocket.accept()
            logging.debug("Client connected: {}:{}".format(
                fromaddr[0], fromaddr[1]))

            conn = ssl.wrap_socket(newsocket,
                                   server_side=True,
                                   certfile=self.server_cert,
                                   keyfile=self.server_key)
            logging.debug("SSL established. Peer: {}".format(
                conn.getpeercert()))
            try:
                request = conn.recv()
                logging.debug("Full request: {}".format(request))
                url = urlparse(request)
                scheme = url.scheme.decode()
                netloc = url.netloc.decode()
                path = url.path.decode().rstrip()
                logging.debug("Scheme: {}".format(scheme))
                logging.debug("Netloc: {}".format(netloc))
                logging.debug("Path: {}".format(path))

                header = get_header()
                body = b""

                cgi = False
                try:
                    for key, val in self.cgi_registry.items():
                        if re.match(key, path):
                            cgi = True
                            env = self.get_env(url, fromaddr[0])
                            script = val
                except:
                    script = None
                    env = None

                if cgi:
                    body = run_cgi(script, env)[0]

                elif os.path.isfile(self.base_path + path):
                    if not path.endswith(".gmi"):
                        header = get_header(
                            '20',
                            mimetypes.guess_type(self.base_path +
                                                 path)[0].encode())
                    cfile = open(self.base_path + path)
                    body = cfile.read().encode()
                    cfile.close()
                elif os.path.isfile(self.base_path + path.rstrip('/') +
                                    '/index.gmi'):
                    cfile = open(self.base_path + path.rstrip('/') +
                                 '/index.gmi')
                    body = cfile.read().encode()
                    cfile.close()
                    logging.debug("Body: {}".format(body))
                elif os.path.isdir(self.base_path +
                                   path) and self.allow_dir_list:
                    body = self.get_dir_list(path)

                else:
                    header = get_header('40', b"File not found")

                conn.write(header + body)
            finally:
                logging.debug("Closing connection")
                conn.shutdown(socket.SHUT_RDWR)
                conn.close()

    def get_dir_list(self, directory):
        contents = b"#Contents:\r\n"
        dirs = []
        files = []
        for mfile in os.listdir(self.base_path + directory):
            if os.path.isdir(os.path.join(self.base_path + directory, mfile)):
                dirs.append(os.path.join(directory, mfile))
            elif os.path.isfile(os.path.join(self.base_path + directory,
                                             mfile)):
                files.append(os.path.join(directory, mfile))
        dirs = sorted(dirs)
        files = sorted(files)
        for entry in dirs:
            contents = contents + b"=> " + entry.encode() + b"\r\n"
        for entry in files:
            contents = contents + b"=> " + entry.encode() + b"\r\n"
        return contents

    def get_env(self, url, remote_addr):
        path = url.path.decode().rstrip()
        query = url.query.decode().rstrip()
        env = {}
        env['GATEWAY_INTERFACE'] = 'CGI/1.1'
        env['GEMINI_DOCUMENT_ROOT'] = str(self.base_path)
        env['GEMINI_URL'] = str(url.geturl().decode().rstrip())
        env['GEMINI_URL_PATH'] = str(path)
        env['PATH_INFO'] = str(path)
        env['PATH_TRANSLATED'] = str(self.base_path + path)
        env['QUERY_STRING'] = str(query)
        env['REMOTE_ADDR'] = str(remote_addr)
        try:
            env['REMOTE_HOST'] = str(
                socket.getfqdn(socket.gethostbyaddr(remote_addr)[0]))
        except:
            env['REMOTE_HOST'] = str(remote_addr)
        env['SERVER_NAME'] = str(socket.getfqdn())
        env['SERVER_PORT'] = str(self.listen_port)
        env['SERVER_PROTOCOL'] = 'GEMINI'
        env['SERVER_SOFTWARE'] = 'gMNd 0.0.1'

        return env


def run_cgi(script, menv):
    """Run a command on system and capture result"""
    process = subprocess.Popen(script,
                               env=menv,
                               shell=True,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    result = process.communicate()
    return result


def get_header(status='20', meta=b"text/gemini"):
    metadict = {}
    metadict['10'] = meta
    metadict['20'] = meta
    metadict['30'] = meta
    metadict['40'] = meta
    metadict['50'] = meta
    metadict['60'] = b"Client certificate required"
    separator = b" "
    terminator = b"\r\n"
    header = bytes(status.encode()) + separator + metadict[status] + terminator
    return header


if __name__ == "__main__":
    options = {}
    if (sys.argv[1] == "-f" or sys.argv[1] == "--file") and sys.argv[2]:
        options['config_file'] = sys.argv[2]
    server = gMNd(options)
    server.run()
