#!/usr/bin/python
# -*- coding: UTF-8 -*-


import re
from tornado.web import RequestHandler
from bson import ObjectId


class BaseRequestHandler(RequestHandler):
    def getDB(self):
        db = self.application.settings['db']
        return db
    def getUser(self):
        db = self.getDB()
        userid = self.get_current_user()       
        return [userid, self.get_secure_cookie("usertype"), self.get_secure_cookie("class_id")]
    def get_current_user(self):
        return self.get_secure_cookie("userid")

class IndexHandler(BaseRequestHandler):
    def get(self):
        user = self.getUser()
        print(user)
        self.render('index.html', user = user)

class ErrorHandler(BaseRequestHandler):
    def get(self):
        self.render('404.html')