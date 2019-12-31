import base64
import numpy as np
from app.base import BaseRequestHandler
import copy
import tornado
import time
from bson.objectid import ObjectId

dates = ["2019.06.24-2019.06.28", "2019.07.01-2019.07.05"]
weeks = ["第一周", "第二周", "第三周", "第四周", "第五周"]
days = ["星期一", "星期二", "星期三", "星期四", "星期五"]
classes_nums = ["第一节课", "第二节课", "第三节课", "第四节课", "第五节课", "第六节课", "第七节课", "第八节课", "第九节课"]
states = ['专注','书写','回答','瞌睡','非学习','无效时间','起立','讨论', '玩手机']
classes_names = ["语文", "数学", "英语", "物理", "化学", "生物", "政治", "历史", "地理"]

class XcxClassesListHandler(BaseRequestHandler):  
    def get(self):
        db = self.getDB()
        classes = db.pg_classes.find({}, {"class_id":1})
        result = [[] for i in range(10)]
        for c in classes:
        	result[int(c["class_id"][0:2])].append(c["class_id"])
        self.finish({"result": result})

class XcxClassReportlistHandler(BaseRequestHandler):
	def get(self):
		db = self.getDB()
		class_id = self.get_argument("class_id")
		c = db.pg_classes.find_one({"class_id": class_id}, {"student_faces": 0})
		eachclass_week = []
		if "lesson_nums" in c:
		    lesson_nums = c["lesson_nums"]
		    for l in lesson_nums:
		        thisweek = int(l["lesson_num"].split("_")[0])
		        if_find = 0
		        for w in eachclass_week:
		            if w["week"] == thisweek and l["points"] != "未检测到学生！":
		                w["points"] += l["points"]
		                w["nums"] += 1
		                if_find = 1
		                break
		        if if_find == 0 and l["points"] != "未检测到学生！":
		            eachclass_week.append({"week": thisweek, "week_date": l["week_date"], "points": l["points"], "nums": 1, "average": 0})
		    for e in eachclass_week:
		        e["average"] = round(e["points"]/e["nums"], 2)
		    eachclass_week = sorted(eachclass_week, key = lambda x: x["week"])
		self.finish({"result": eachclass_week})

class XcxClassReportdetailHandler(BaseRequestHandler):
	def get(self):
		db = self.getDB()
		class_id = self.get_argument("class_id")
		week_num = int(self.get_argument("week"))
		classes = db.pg_classes.find_one({"class_id": class_id}, {"student_faces": 0})
		lesson_nums = classes["lesson_nums"]
		lessons = []
		state_array = [[0 for i in range(10)] for j in range(5)]
		week_state_array = [0 for i in range(10)]
		for l in lesson_nums:
			lesson_array = l["lesson_num"].split("_")
			lesson_array = list(map(int, lesson_array))			
			if lesson_array[0] == week_num:
				if l["points"] != "未检测到学生！":
					lesson_array.append(round(l["points"], 2))
				else:
					lesson_array.append(l["points"])
				ps = db.pg_students_performances.find({"lesson_num": l["lesson_num"], "class_id": class_id}, {"state_array": 1})
				for p in ps:
					state_array[lesson_array[1]-1] = [(state_array[lesson_array[1]-1][i] + p["state_array"][i]) for i in range(10)]
				lessons.append(lesson_array[1:])
		lessons = sorted(lessons, key = lambda x: (x[0], x[1]))
		for s in state_array:
			week_state_array = [(week_state_array[i] + s[i]) for i in range(10)]
		total_states = sum(week_state_array)
		states_pingjia = []
		zhuanzhu = round(float(week_state_array[0] + week_state_array[1] + week_state_array[2] + week_state_array[5])/total_states*100, 2)
		states_pingjia.append(pingjia(zhuanzhu, 85, 60))
		hudong = round(float(week_state_array[2] + week_state_array[5])/total_states*100, 2)
		states_pingjia.append(pingjia(hudong, 5, 1))
		feixuexi = round(float(week_state_array[3] + week_state_array[4])/total_states*100, 2)
		states_pingjia.append(pingjia(feixuexi, 15, 5))
		buqueding = round(float(week_state_array[6])/total_states*100, 2)
		states_pingjia.append(pingjia(buqueding, 15, 5))
		self.finish({"lessons": lessons, "state_array": state_array, "week_state_array": week_state_array, "pingjia": states_pingjia})

class XcxEachLessonReportHandler(BaseRequestHandler):
	def get(self):
		db = self.getDB()
		class_id = self.get_argument("class_id")
		lesson_num = self.get_argument("lesson_num")
		class_info = db.pg_classes.find_one({"class_id": class_id}, {"student_faces": 0})
		students = []
		each_points = []
		lesson_points = [{"points":0.0, "nums":0, "average":0.0, "time": i} for i in range(45)]
		total_states = [0 for i in range(10)]
		for s in class_info["students"]:
			si = {}
			true_sti = db.pg_students.find_one({"student_id": s, "class_id": class_id})
			for sti in true_sti:
				if sti != "_id":
					si[sti] = true_sti[sti]
			students.append(si)
			stu_per = db.pg_students_performances.find_one({"StudentID": s,"class_id": class_id, "lesson_num": lesson_num}, projection={'points': True, "confirm_faces_states":True, "timeline": True, "state_array": True})
			if len(stu_per["confirm_faces_states"]) == 0:
				each_points.append(101)
			else:
				each_points.append(round(stu_per["points"],2))
				for sa_index, sa in enumerate(stu_per["state_array"]):
					total_states[sa_index] += sa
				for t in stu_per["timeline"]:
					total_number = 0
					total_points = 0
					for index,n in enumerate(t["state"]):
						if index in [0, 1]:
							total_points += n * 2
						if index in [2, 5, 6, 7, 8, 9]:
							total_points += n 
						total_number += n
					lesson_points[int(t["time"])]["nums"] += 1
					lesson_points[int(t["time"])]["points"] += round(float(total_points)/float(total_number*2) * 100, 2)
		true_lesson_points = []
		for l in lesson_points:
			if l["nums"] != 0:
				l["average"] = round(l["points"]/l["nums"], 2)
				true_lesson_points.append(l)
		self.finish({"students": students, "students_points": each_points, "state_array": total_states, "lesson_points": true_lesson_points})

class XcxStudentEachLessonReportHandler(BaseRequestHandler):
	def get(self):
		db = self.getDB()
		class_id = self.get_argument("class_id")
		student_id = self.get_argument("student_id")
		lesson_num = self.get_argument("lesson_num")
		performance = db.pg_students_performances.find_one({"StudentID": student_id,"class_id": class_id, "lesson_num": lesson_num}, projection={'points': True, "timeline": True, "state_array": True})
		pics = db.pg_students_performances_imgs.find_one({"StudentID": student_id,"class_id": class_id, "lesson_num": lesson_num})
		timeline_index = []
		timeline_points = []
		for t in performance["timeline"]:
			timeline_index.append(t["time"])
			total_number = 0
			total_points = 0
			for index,n in enumerate(t["state"]):
				if index in [0, 1]:
					total_points += n * 2
				if index in [2, 5, 6, 7, 8, 9]:
					total_points += n 
				total_number += n
			timeline_points.append(round(float(total_points)/float(total_number*2) * 100, 2))
		total_states = sum(performance["state_array"])
		sa = performance["state_array"]
		states_pingjia = []
		zhuanzhu = round(float(sa[0] + sa[1] + sa[2] + sa[5])/total_states*100, 2)
		states_pingjia.append(pingjia(zhuanzhu, 85, 60))
		hudong = round(float(sa[2] + sa[5])/total_states*100, 2)
		states_pingjia.append(pingjia(hudong, 5, 1))
		feixuexi = round(float(sa[3] + sa[4])/total_states*100, 2)
		states_pingjia.append(pingjia(feixuexi, 15, 5))
		buqueding = round(float(sa[6])/total_states*100, 2)
		states_pingjia.append(pingjia(buqueding, 15, 5))
		abnormal_pics = pics["abnormal_pics"]["4"][:6] + pics["abnormal_pics"]["5"][-6:] 
		for pic in abnormal_pics:
			pic["time"] = [int(pic["time"]/120) ,int(pic["time"]%120/2)]
		self.finish({"timeline_index": timeline_index, "timeline_points": timeline_points, "state_array": sa, "states_pingjia": states_pingjia, "abnormal_pics": abnormal_pics})

class XcxSearchHandler(BaseRequestHandler):
	def get(self):
		db = self.getDB()
		classes = db.pg_classes.find({}, {"student_faces": 0})
		result = []
		for c in classes:
			class_info = {}
			if "lesson_nums" in c:
				for k in c:
					if k != "_id":
						class_info[k] = c[k]
				result.append(class_info)
		self.finish({"result": result})
	def post(self):
		result = {"student_name": "", "student_image": "", "points": 0, "week_date": ""}
		db = self.getDB()
		class_id = self.get_argument("class_id")
		student_id = self.get_argument("student_id")
		lesson_num = self.get_argument("lesson_num")
		student = db.pg_students.find_one({"student_id": student_id, "class_id": class_id})
		performance = db.pg_students_performances.find_one({"StudentID": student_id,"class_id": class_id, "lesson_num": lesson_num}, projection={'points': True, "confirm_faces": True, "week_date": True})
		if len(performance["confirm_faces"]) == 0:
			result["points"] = 101
		else:
			result["points"] = round(performance["points"], 2)
			result["week_date"] = performance["week_date"]
			result["student_name"] = student["student_name"]
			result["student_image"] = student["student_image"]
		self.finish(result)


def pingjia(points, maxp, minp):
    if points > maxp:
        return {"point": points, "pingjia": 0}
    elif points > minp:
        return {"point": points, "pingjia": 1}
    else:
        return {"point": points, "pingjia": 2}