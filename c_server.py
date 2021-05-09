import http.server
import pathlib
import sys
import argparse
import random
import math
from urllib import parse
import re
import ssl
import threading
import collections
import json

DEFAULT_PORT = 7999
DEFAULT_HOST = "127.0.0.1";

class Har:
    def __init__(self, har = None):
        self.har = har;

    def set(self, har):
        self.har = har;

    def wait_set(self):
        while not self.har:
            pass;

        return self.har;

class Queue(collections.deque):
    def push(self):
        har = Har();
        self.append(har);
        return har;


def request_handler_factory(queue):

    class RequestHandler (http.server.BaseHTTPRequestHandler):
        
        def __init__(self, *pargs, **kwargs):
            self.queue = queue;
            self.cur = None;
            super().__init__(*pargs, **kwargs);

        def do_GET (self):
            self.log_req();
            self.send_response (200)
            try:
                self.cur = self.queue.popleft();
                data = {"cookies": True, "url": "https://www.nouonline.net/"};

            except IndexError:
                data = {};
            
            data = json.dumps(data);

            self.send_header ('Content-Length', len(data))

            self.send_header ('Content-Type', 'application/json')

            self.end_headers ()

            self.wfile.write (bytes(data, encoding = "utf8"));

        def do_POST (self):
            self.log_req();
            self.send_response (200)

            data = {};

            if self.cur:
               pdata = json.loads(self.data);
               self.cur.set(pdata["har"]);
               data["ok"] = True; 

            data = json.dumps(data);

            self.send_header ('Content-Length', len(data))

            self.send_header ('Content-Type', 'application/json')

            self.end_headers ()

            self.wfile.write (bytes(data, encoding = "utf8"));


        def log_req (self):
            print ('''url: %s
    method: %s
    headers: %a''' % (self.path, self.command, dict (self.headers)))
            
            self.data = self.rfile.read (int (self.headers.get ('content-length', 0))).decode ()

            if self.data:
                print ('data:', self.data)

        class MessageClass (http.server.BaseHTTPRequestHandler.MessageClass):

            def __iter__ (self):
                
                for t in zip (self.keys, self.values):
                    yield t

            def __next__ (self):
                return self.__iter__ ()

    return RequestHandler;

que = Queue([]);
server = http.server.HTTPServer ((DEFAULT_HOST, DEFAULT_PORT), request_handler_factory(que));

thd = threading.Thread(target = server.serve_forever, daemon = True);
thd.start();
print("started server");
try:

    hars = [];

    hars.append(que.push().wait_set());
    hars.append(que.push().wait_set());
    hars.append(que.push().wait_set());

except KeyboardInterrupt:
    server.shutdown();

for har in hars:
    print(har.har)
