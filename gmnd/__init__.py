import logging
import mimetypes
import os
import socket
import ssl
import sys
from socket import AF_INET, SHUT_RDWR, SO_REUSEADDR, SOCK_STREAM, SOL_SOCKET
from urllib.parse import urlparse


class gMNd:
    def __init__(self, options={}):
        self.base_path = options.get('base_path', './content')
        self.logg_level = options.get('logg_level', logging.INFO)
        self.listen_addr = options.get('listen_addr', '127.0.0.1')
        self.allow_dir_list = options.get('allow_dir_list', False)
        self.listen_port = options.get('listen_port', 1965)
        self.server_cert = options.get('server_cert', './certs/cert.pem')
        self.server_key = options.get('server_key', './certs/cert.key')
        logging.basicConfig(stream=sys.stderr, level=self.logg_level)
        self.bindsocket = socket.socket()

        self.bindsocket.bind((self.listen_addr, self.listen_port))
        self.bindsocket.listen(5)

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
                logging.debug(request)
                url = urlparse(request)
                scheme = url.scheme.decode()
                netloc = url.netloc.decode()
                path = url.path.decode().rstrip()
                logging.debug(scheme)
                logging.debug(netloc)
                logging.debug(path)

                header = get_header()
                body = b""
                if os.path.isfile(self.base_path + path):
                    if not path.endswith(".gmi"):
                        header = get_header(
                            '20',
                            mimetypes.guess_type(
                                self.base_path + path)[0].encode())
                    cfile = open(self.base_path + path)
                    body = cfile.read().encode()
                    cfile.close()
                elif os.path.isfile(self.base_path + path.rstrip('/') +
                                    '/index.gmi'):
                    cfile = open(self.base_path + path.rstrip('/') +
                                 '/index.gmi')
                    body = cfile.read().encode()
                    cfile.close()
                    logging.debug(body)
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
    server = gMNd({
        'allow_dir_list': True,
        'listen_addr': '0.0.0.0'
    })
    server.run()
