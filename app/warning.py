from app.base import BaseRequestHandler
import tornado,os,time
from tornado.websocket import WebSocketHandler
import subprocess
class WarningIndexHandler(BaseRequestHandler):
    @tornado.web.authenticated
    def get(self):
        user = self.getUser()
        db = self.getDB()
        classes = db.pg_realtimewarning.find()
        self.render('warningsys/index.html', user = user, classes = classes)

class ClassDetailHandler(BaseRequestHandler):
    @tornado.web.authenticated
    def get(self):
        user = self.getUser()
        db = self.getDB()
        class_id = self.get_argument("class_id")
        thisclass = db.pg_realtimewarning.find_one({"class_id": class_id})
        self.render('warningsys/class_detail.html', user = user, thisclass = thisclass)

class FasterHandler(WebSocketHandler):    
    def open(self):
        p = subprocess.Popen("CUDA_VISIBLE_DEVICES=1 python3 app/faster/front_back_frame.py", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) 
        lines = [] 
        for line in iter(p.stdout.readline, b''): 
            if line[0:2] == "[[" or line[0:3] == "img": 
                self.write_message(line)

    def on_message(self, message):
        pass

class GetFasterHandler(BaseRequestHandler):
    def get(self):
        user = self.getUser()
        db = self.getDB()
        timestamp = self.get_argument("timestamp")
        class_id = self.get_argument("class_id")
        result = db.pg_realtimewarning.find_one({"class_id":class_id})
        if result["time"] == timestamp:
            self.finish("no result")
        else:
            self.finish({"imgs":result["imgs"],"warningimgs":result["warningimgs"],"time":result["time"],"states":result["states"],"cur_boxes":result["cur_boxes"]})

class StartAnalyseHandler(BaseRequestHandler):
    def get(self):
        user = self.getUser()
        db = self.getDB()
        class_id = self.get_argument("class_id")
        class_detail = db.pg_realtimewarning.find_one({"class_id":class_id})
        if class_detail["state"] == 1:
            self.finish("error")
        else:
            nvidia_smi = int(os.popen('nvidia-smi -q -i 0 -d MEMORY | grep Free').readlines()[0].split(":")[1].split("M")[0])
            if nvidia_smi < 5000:
                self.finish("not enough memory") 
            else:
                progress = os.popen("nohup python3 app/faster/front_back_frame.py --stream " + class_detail["stream"] + " --token " + class_detail["token"] + " --class-id " + class_id + "> " + class_id + ".file 2>&1 &")
                pid_progress = os.popen("ps -ef | grep " + class_detail["token"])
                for p in pid_progress.readlines():
                    p_parts = p.split( )
                    if p_parts[7] == "python3":
                        pid = p_parts[1]
                        break
                db.pg_realtimewarning.update_one({"class_id": class_id}, {"$set": {"state": 1, "pid": pid}})
                self.finish("success")

class StopAnalyseHandler(BaseRequestHandler):
    def get(self):
        user = self.getUser()
        db = self.getDB()
        class_id = self.get_argument("class_id")
        class_detail = db.pg_realtimewarning.find_one({"class_id":class_id})
        pid = class_detail["pid"]
        if class_detail["state"] == 0:
            self.finish("error")
        else:
            progress = os.popen("kill -9 " + pid)
            if_success = 1
            for p in progress.readlines():
                if "没有那个进程" in p:
                    if_success = 0
                    break
            if if_success == 0:
                self.finish("error")
            else:
                db.pg_realtimewarning.update_one({"class_id": class_id}, {"$set": {"state": 0}})
                self.finish("success")