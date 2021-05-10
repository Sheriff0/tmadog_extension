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


class DogCookieClient(http.server.HTTPServer):
    def __init__(self, *pargs, **kwargs):
        self.request_queue = collections.deque([]);
        self.cur = Har("dummy");
        super().__init__(*pargs, **kwargs);

    def push(self):
        har = Har();
        self.request_queue.append(har);
        return har;

    def _pop(self):
        self.cur = self.request_queue.popleft();
        return self.cur;


class RequestHandler (http.server.BaseHTTPRequestHandler):
    
    def do_GET (self):
        self.log_req();
        self.send_response (200);

        if self.server.cur.har != None:
            try:
                self.server._pop();
                data = {"cookies": True, "url": "https://www.nouonline.net/"};
                print("sending new cookie request");

            except IndexError:
                data = {};
        else:
            data = {"cookies": True, "url": "https://www.nouonline.net/"};
            print("resending previous cookie request");
        

        data = json.dumps(data);

        self.send_header ('Content-Length', len(data))

        self.send_header ('Content-Type', 'application/json')

        self.end_headers ()

        self.wfile.write (bytes(data, encoding = "utf8"));

    def do_POST (self):
        self.log_req();
        self.send_response (200)

        data = {"ok": False};

        if self.server.cur.har == None:
            try:
               pdata = json.loads(self.data);
               if not "har" in pdata:
                   raise json.decoder.JSONDecodeError();

               print("recieved har, setting...");
               self.server.cur.set(pdata);
               data["ok"] = True; 

            except json.decoder.JSONDecodeError:
                data["ok"] = False; 
                print('recieved invalid data %s' % (self.data,));

        data = json.dumps(data);

        self.send_header ('Content-Length', len(data))

        self.send_header ('Content-Type', 'application/json')

        self.end_headers ()

        self.wfile.write (bytes(data, encoding = "utf8"));


    def log_req (self):
        print ('''\n\nurl: %s
method: %s
headers: %a''' % (self.path, self.command, dict (self.headers)))
        
        self.data = self.rfile.read (int (self.headers.get ('content-length', 0))).decode ()

        if self.data:
            print ('\ndata:', self.data)

    class MessageClass (http.server.BaseHTTPRequestHandler.MessageClass):

        def __iter__ (self):
            
            for t in zip (self.keys, self.values):
                yield t

        def __next__ (self):
            return self.__iter__ ()


server = DogCookieClient((DEFAULT_HOST, DEFAULT_PORT), RequestHandler);

thd = threading.Thread(target = server.serve_forever, daemon = True);
thd.start();
print("started server");
try:

    hars = [];

    hars.append(server.push().wait_set());
    hars.append(server.push().wait_set());
    hars.append(server.push().wait_set());

except KeyboardInterrupt:
    pass;

server.shutdown();

for har in hars:
    print(har)
