#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os.path
import tornado.httpserver
import tornado.ioloop
import tornado.options
from tornado.options import define, options
import urls 
import pymongo

if __name__ == '__main__':
    tornado.options.parse_command_line()  
    conn = pymongo.MongoClient('localhost',27017)
    db = conn['test']       
    tornado.options.parse_command_line()  
    settings = {
        "template_path": os.path.join(os.path.dirname(__file__), "template"),
        "static_path": os.path.join(os.path.dirname(__file__), "static"),
        "cookie_secret": "bZJc2sWbQLKos6GkHn/VB9oXwQt8S0R0kRvJ5/xJ89E=",
        "debug": True,
#        "xsrf_cookies": True,
        "login_url": "/signin",
        'db': db,
    }
    app = tornado.web.Application(urls.handlers, **settings)
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(8000)
    tornado.ioloop.IOLoop.instance().start()
