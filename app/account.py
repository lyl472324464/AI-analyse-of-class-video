#!/usr/bin/python
# -*- coding: UTF-8 -*-

from app.base import BaseRequestHandler

zhanghao = {"zcxx":{"password":"123456", "type": "m", "class_id": "0201"},
            "lihonglai":{"password":"13920890036", "type": "m", "class_id": "0201"},
            "gongyushui":{"password":"13072266220", "type": "m", "class_id": "0201"},
            "liqun":{"password":"13032285726", "type": "m", "class_id": "0201"},
            "miyingping":{"password":"13821402009", "type": "m", "class_id": "0201"},
            "wangxin":{"password":"13702050639", "type": "m", "class_id": "0201"},
            "hejinhuan":{"password":"13032218051", "type": "m", "class_id": "0201"},
            "liuyuzhen":{"password":"18622115212", "type": "t", "class_id": "0107"},
            "wuwenting":{"password":"18222916025", "type": "t", "class_id": "0108"},
            "mengfanlian":{"password":"15692297970", "type": "t", "class_id": "0109"},
            "liuzhaojing":{"password":"15732861731", "type": "t", "class_id": "0110"},
            "caoqiuchen":{"password":"18522880056", "type": "t", "class_id": "0111"},
            "liuzhaojing2":{"password":"15732861731", "type": "t", "class_id": "0112"},
            }
account_type = {"t": "老师", "m": "校长", "s": "学生"}
class SignInHandler(BaseRequestHandler):
    def get(self):
        try:
            next_page = self.get_argument("next")
        except:
            next_page = "/"
        self.render('account/sign_in.html', next_page = next_page)
    def post(self):    
        username = self.get_argument("username")
        a_type = self.get_argument("type")
        password = self.get_argument("password")
        next_page = self.get_argument("next")
        try:
            if zhanghao[username]["password"] == password and zhanghao[username]["type"] == a_type:                
                self.set_secure_cookie("userid", username, expires_days=None)
                self.set_secure_cookie("usertype", a_type, expires_days=None)
                self.set_secure_cookie("class_id", zhanghao[username]["class_id"], expires_days=None)
                if username == "dx":
                    self.redirect("/dxclasseslist")
                elif next_page != '':
                    if next_page == "/dxclasseslist":
                        if a_type == "t":
                            self.redirect("/dxeachclass?class_id=" + zhanghao[username]["class_id"])
                        elif a_type == "m":
                            self.redirect(next_page)
                    elif next_page == "/warning":
                        if a_type == "t":
                            self.redirect("/wcd?class_id=" + zhanghao[username]["class_id"])
                        elif a_type == "m":
                            self.redirect(next_page)
                    else:
                        self.redirect(next_page)
                elif username == "zhuyuan":
                    self.redirect("/bf?ClassID=201")
                elif a_type == "m":
                    self.redirect("/")
                elif a_type == "t":
                    self.redirect("/")
                else:
                    self.redirect("/")
            else:
                self.finish("密码错误或权限不足，怀疑非法入侵，您的IP将被记录并跟踪")    
        except:
            self.finish("账号不存在")       
                        

class SignUpHandler(BaseRequestHandler):
    def get(self):
        self.render('account/sign_up.html')

class SignOutHandler(BaseRequestHandler):
    def get(self):
        self.clear_cookie("userid")
        self.clear_cookie("usertype")
        self.redirect("/")

class MyAccountHandler(BaseRequestHandler):
    def get(self):
        user = self.getUser()
        user_type = zhanghao[user[0]]["type"]
        self.render('account/my_account.html', user = user, user_type = user_type, account_type = account_type)

class AdviseHandler(BaseRequestHandler):
    def get(self):
        user = self.getUser()
        user_type = zhanghao[user]["type"]
        self.render('account/advise.html', user = user, user_type = user_type, account_type = account_type)

class ChangePasswordHandler(BaseRequestHandler):
    def get(self):
        user = self.getUser()
        user_type = zhanghao[user]["type"]
        self.render('account/changepassword.html', user = user, user_type = user_type, account_type = account_type)