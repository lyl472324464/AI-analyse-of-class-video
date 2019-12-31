#!/usr/bin/python
# -*- coding: UTF-8 -*-
import base64
import numpy as np
from app.base import BaseRequestHandler
import copy
import tornado
import time
from bson.objectid import ObjectId

dates = ["2019.06.24-2019.06.28", "2019.07.01-2019.07.05"]
weeks = ["第一周", "第二周", "第三周", "第四周", "第五周", "第六周", "第七周", "第八周", "第九周", "第十周", "第十一周", "第十二周", "第十三周", "第十四周", "第十五周", "第十六周", "第十七周"]
days = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
classes_nums = ["第一节课", "第二节课", "第三节课", "第四节课", "第五节课", "第六节课", "第七节课", "第八节课", "第九节课"]
states = ['专注','书写','回答','瞌睡','非学习','无效时间','起立','讨论', '玩手机']
classes_names = ["语文", "数学", "英语", "物理", "化学", "生物", "政治", "历史", "地理", "自习", "音乐", "信息", "体育", "美术"]

class XZHandler(BaseRequestHandler):
    @tornado.web.authenticated  
    def get(self):
        user = self.getUser()
        db = self.getDB()
        SchoolID = self.get_argument("SchoolID")
        school = db.school.find_one({"school_id": SchoolID})
        classes = db.classes.find({"school_id": SchoolID})
        self.render("view/xz.html", user = user, school = school, classes_names = classes_names)

class SchoolInfoHandler(BaseRequestHandler):
    @tornado.web.authenticated  
    def get(self):
        user = self.getUser()
        db = self.getDB()
        SchoolID = self.get_argument("SchoolID")
        school = db.school.find_one({"school_id": SchoolID})
        classes = db.classes.find({"school_id": SchoolID})
        g1 = []
        g2 = []
        g3 = []
        points = [[0 for i in range(3)] for i in range(4)]
        for c in classes:
            gn = c["class_id"].split("_")[1]
            cn = c["class_id"].split("_")[2]
            points[int(cn) - 1][int(gn) - 1] = round(c["points"],2)
            if gn == "1":
                g1.append(copy.deepcopy(c))
            elif gn == "2":
                g2.append(copy.deepcopy(c))
            elif gn == "3":
                g3.append(copy.deepcopy(c))
        self.render("view/school_info.html", user = user, school = school, g1 = g1, g2 = g2, g3 = g3, points = points, classes_names = classes_names)

class SchoolInfoEachKindClassHandler(BaseRequestHandler):
    @tornado.web.authenticated  
    def get(self):
        user = self.getUser()
        db = self.getDB()
        SchoolID = self.get_argument("SchoolID")
        school = db.school.find_one({"school_id": SchoolID})
        final_points = []
        for i in range(1,4):
            points = [[0 for jj in range(9)] for ii in range(4)]
            for j in range(1,5):
                for index,cn in enumerate(classes_names):                
                    ps = db.students_performances.find({"class_id": "g_" + str(i) + "_" + str(j), "lesson_name": cn}, {'points': 1})
                    length = 0
                    sums = 0
                    for p in ps:
                        length += 1
                        sums += p["points"]
                    if length != 0:
                        points[j - 1][index] = sums/length
            final_points.append(copy.deepcopy(points))
        self.render("view/school_infoeachkindclass.html", user = user, school = school, points = final_points, classes_names = classes_names)

class GradeInfoHandler(BaseRequestHandler):
    @tornado.web.authenticated  
    def get(self):
        user = self.getUser()
        db = self.getDB()
        GradeID = self.get_argument("GradeID")
        SchoolID = self.get_argument("SchoolID")
        classes = db.classes.find({"school_id": SchoolID})
        cpoints = [0 for i in range(4)]
        for c in classes:
            gn = c["class_id"].split("_")[1]
            cn = c["class_id"].split("_")[2]            
            if gn == "1":
                cpoints[int(cn) - 1] = round(c["points"],2)
        points = [[0 for jj in range(9)] for ii in range(4)] 
        state_array = []
        state_array_c = []      
        for j in range(1,5):
            sa = [ 0 for s in range(8) ]
            sa_c = []
            for index,cn in enumerate(classes_names):                
                ps = db.students_performances.find({"class_id": "g_" + str(1) + "_" + str(j), "lesson_name": cn}, {'points': 1, 'state_array': 1})
                sa_cc = [ 0 for s in range(8) ]
                length = 0
                sums = 0
                for p in ps:
                    sa = list(map(lambda x: x[0]+x[1], zip(sa, p["state_array"])))
                    sa_cc = list(map(lambda x: x[0]+x[1], zip(sa_cc, p["state_array"])))
                    length += 1
                    sums += p["points"]
                if length != 0:
                    points[j - 1][index] = sums/length
                    sa_c.append(sa_cc)
            state_array.append(sa)
            state_array_c.append(sa_c)
        self.render("view/grade_info.html", user = user, lpoints = [82.56, 76.39, 82.58, 73.29], cpoints = cpoints, points = points, classes_names = classes_names, state_array = state_array, state_array_c = state_array_c)

class GetStudentTimelinePicHandler(BaseRequestHandler):
    @tornado.web.authenticated      
    def get(self):
        user = self.getUser()
        db = self.getDB()
        PerformanceID = self.get_argument("PerformanceID")
        TimeNum = self.get_argument("TimeNum")
        pic = db.students_performances.find_one({"_id": ObjectId(PerformanceID)}, projection={'timeline': True})["timeline"][int(TimeNum)]["pic"]
        self.finish(pic)

class StudentEachLessonPerformanceHandler(BaseRequestHandler):
    @tornado.web.authenticated      
    def get(self):
        user = self.getUser()
        db = self.getDB()
        StudentID = self.get_argument("StudentID")
        LessonNum = self.get_argument("LessonNum")
        lesson_name = days[int(LessonNum.split("_")[0]) - 1] + classes_nums[int(LessonNum.split("_")[1]) - 1]
        student = db.students.find_one({"student_id": StudentID})
        class_info = db.classes.find_one({"class_id": student["class_id"]})
        performance = db.students_performances.find_one({"StudentID": StudentID, "lesson_num": LessonNum})
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
        students_points = student["points"]
        class_points = class_info["lessons"][int(LessonNum.split("_")[0]) - 1][int(LessonNum.split("_")[1]) - 1]["points"]
        total_states = sum(performance["state_array"])
        sa = performance["state_array"]
        states_pingjia = []
        if performance["state_array"][6] > 0:
            zhuanzhu = round(float(sa[0] + sa[1] + sa[2] + sa[5])/total_states*100, 2)
            states_pingjia.append(pingjia(zhuanzhu, 85, 60))
            hudong = round(float(sa[2] + sa[5])/total_states*100, 2)
            states_pingjia.append(pingjia(hudong, 5, 1))
            feixuexi = round(float(sa[3] + sa[4])/total_states*100, 2)
            states_pingjia.append(pingjia(feixuexi, 15, 5))
            buqueding = round(float(sa[6])/total_states*100, 2)
            states_pingjia.append(pingjia(buqueding, 15, 5))
        else:
            zhuanzhu = round(float(sa[0] + sa[1] + sa[2])/total_states*100, 2)
            states_pingjia.append(pingjia(zhuanzhu, 85, 60))
            hudong = round(float(sa[2])/total_states*100, 2)
            states_pingjia.append(pingjia(hudong, 5, 1))
            feixuexi = round(float(sa[3] + sa[4])/total_states*100, 2)
            states_pingjia.append(pingjia(feixuexi, 15, 5))
            buqueding = round(float(sa[5])/total_states*100, 2)
            states_pingjia.append(pingjia(buqueding, 15, 5))
        if performance == None:
        	self.finish("no performance")
        else:
        	self.render('view/studenteachlesson.html', user = user, states_pingjia = states_pingjia, timeline_index = timeline_index, timeline_points = timeline_points, students_points = students_points, class_points = class_points, lesson_name = lesson_name, class_info = class_info, student = student, performance = performance, np = np, states = states)

class StudentEachWeekEachKindClassPerformanceHandler(BaseRequestHandler):
    @tornado.web.authenticated  
    def get(self):
        user = self.getUser()
        db = self.getDB()
        StudentID = self.get_argument("StudentID")
        WeekID = self.get_argument("WeekID")
        student = db.students.find_one({"student_id": StudentID})
        class_info = db.classes.find_one({"class_id": student["class_id"]})
        points = []
        for cn in classes_names:
            point = []
            ps = db.students_performances.find({"class_id": student["class_id"], "StudentID": StudentID, "lesson_name": cn}, projection={'points': True})
            for p in ps:
                point.append(p["points"])
            points.append(copy.deepcopy(point))
        new_points = []
        for p in points:
            new_points.append(round(np.mean(p),2))
        self.render('view/studenteachweekeachkindclass.html', user = user, points = new_points, student = student, class_info = class_info, classes_nums = classes_nums, days = days)

class StudentEachWeekPerformanceHandler(BaseRequestHandler):
    @tornado.web.authenticated  
    def get(self):
        user = self.getUser()
        db = self.getDB()
        StudentID = self.get_argument("StudentID")
        WeekID = self.get_argument("WeekID")
        student = db.students.find_one({"student_id": StudentID})
        class_info = db.classes.find_one({"class_id": student["class_id"]})
        bar_data = [0 for i in range(5)]
        for s in student["points_each_class"]:
            for sl in s:
                if sl >=90:
                    bar_data[4] += 1
                elif sl >= 80 and sl < 90:
                    bar_data[3] += 1
                elif sl >= 70 and sl < 80:
                    bar_data[2] += 1
                elif sl >= 60 and sl < 70:
                    bar_data[1] += 1
                elif sl < 60:
                    bar_data[0] += 1
        self.render('view/studenteachweek.html', user = user, bar_data = bar_data, student = student, class_info = class_info, classes_nums = classes_nums, days = days)

class ClassInfoEachWeekHandler(BaseRequestHandler):
    @tornado.web.authenticated  
    def get(self):
        user = self.getUser()
        db = self.getDB()
        ClassID = self.get_argument("ClassID")
        WeekID = self.get_argument("WeekID")
        class_info = db.classes.find_one({"class_id": ClassID})
        students = db.students.find({"class_id": ClassID})
        bar_data = [0 for i in range(5)]
        for s in class_info["lessons"]:
            for sl in s:
                if sl["points"] >=90:
                    bar_data[4] += 1
                elif sl["points"] >= 80 and sl["points"] < 90:
                    bar_data[3] += 1
                elif sl["points"] >= 70 and sl["points"] < 80:
                    bar_data[2] += 1
                elif sl["points"] >= 60 and sl["points"] < 70:
                    bar_data[1] += 1
                elif sl["points"] < 60:
                    bar_data[0] += 1
        self.render('view/class_info_eachweek.html', user = user, bar_data = bar_data, class_info = class_info, students = students, classes_nums = classes_nums, days = days)

class ClassInfoEachWeekEachKindClassHandler(BaseRequestHandler):
    @tornado.web.authenticated  
    def get(self):
        user = self.getUser()
        db = self.getDB()
        ClassID = self.get_argument("ClassID")
        WeekID = self.get_argument("WeekID")
        class_info = db.classes.find_one({"class_id": ClassID})
        students = db.students.find({"class_id": ClassID})
        points = []
        for cn in classes_names:
            point = []
            ps = db.students_performances.find({"class_id": ClassID, "lesson_name": cn}, projection={'points': True})
            for p in ps:
                point.append(p["points"])
            points.append(copy.deepcopy(point))
        new_points = []
        for p in points:
            new_points.append(round(np.mean(p),2))
        self.render('view/class_info_eachweekeachkindclass.html', user = user, points = new_points, class_info = class_info, students = students, classes_nums = classes_nums, days = days)

class ClassInfoEachLessonHandler(BaseRequestHandler):
    @tornado.web.authenticated  
    def get(self):
        user = self.getUser()
        db = self.getDB()
        ClassID = self.get_argument("ClassID")
        LessonNum = self.get_argument("LessonNum")
        lesson_name = days[int(LessonNum.split("_")[0]) - 1] + classes_nums[int(LessonNum.split("_")[1]) - 1]
        class_info = db.classes.find_one({"class_id": ClassID})
        students = db.students.find({"class_id": ClassID})
        points = class_info["lessons"][int(LessonNum.split("_")[0]) - 1][int(LessonNum.split("_")[1]) - 1]["points"]
        bar_data = [0 for i in range(5)]
        each_points = []
        for s in students:
            each_points.append(db.students_performances.find_one({"StudentID": s["student_id"],"class_id": ClassID, "lesson_num": LessonNum}, projection={'points': True})["points"])
        students = db.students.find({"class_id": ClassID})
        for sl in db.students_performances.find({"class_id": ClassID, "lesson_num": LessonNum}, projection={'points': True}):
            if sl["points"] >=90:
                bar_data[4] += 1
            elif sl["points"] >= 80 and sl["points"] < 90:
                bar_data[3] += 1
            elif sl["points"] >= 70 and sl["points"] < 80:
                bar_data[2] += 1
            elif sl["points"] >= 60 and sl["points"] < 70:
                bar_data[1] += 1
            elif sl["points"] < 60:
                bar_data[0] += 1
        self.render('view/class_info_eachlesson.html', user = user, each_points = each_points, bar_data = bar_data, points = points, lesson_num = LessonNum, lesson_name = lesson_name, class_info = class_info, students = students)

class ClassInfoBFHandler(BaseRequestHandler):
    @tornado.web.authenticated  
    def get(self):
        user = self.getUser()
        db = self.getDB()
        ClassID = self.get_argument("ClassID")
        class_info = db.classes.find_one({"class_id": ClassID})
        students = db.students.find({"class_id": ClassID})
        s_array = ["201513011418", "201613011606", "201613011618", "201613011409", "201613011513", "201513011603", "201613011511",
        "201513011616", "201613011412", "201613011516", "201613011610", "201613011601", "201613011411", "201613011615", "201513011404", "201613011413",
        "201613011620", "201613011611", "201613011608", "201513011402", "201613011403", "201613011416", "201513011520", "201613011405", "201613011402", "201613011508","201613011613", "201613011404"
        , "201513011403", "201613011604", "201613011512", "201613011616", "201613011414"]
        self.render('view/class_info_bf.html', user = user, class_info = class_info, students = students, s_array = s_array)

class StudentBFHandler(BaseRequestHandler):
    @tornado.web.authenticated  
    def get(self):
        user = self.getUser()
        db = self.getDB()
        ClassID = self.get_argument("ClassID")
        StudentID = self.get_argument("StudentID")
        class_info = db.classes.find_one({"class_id": ClassID})
        student = db.students.find_one({"student_id": StudentID})
        performance = db.students_performances.find_one({"StudentID": StudentID})
        self.render('view/student_bf.html', user = user, class_info = class_info, student = student, performance = performance, np = np, states = states)

class KaoQinBF(BaseRequestHandler):
    @tornado.web.authenticated  
    def get(self):
        user = self.getUser()
        db = self.getDB()
        kch = self.get_argument("kch")
        time = self.get_argument("time")
        kaoqin = db.bf_kaoqin.find_one({"kch": kch, "time": time}, {"kaoqinjieguo": 0})
        number = len(kaoqin["shidao"])
        shidao = kaoqin["shidao"]
        students = []
        for s in kaoqin["shangkexuesheng"]:
            students.append(db.bf_students.find_one({"xh": s}))
        self.render('view/bf_kaoqin.html', kaoqin = kaoqin, students = students, number = number, shidao = shidao)

class GetKaoQinImgBF(BaseRequestHandler):
    @tornado.web.authenticated  
    def get(self):
        user = self.getUser()
        db = self.getDB()
        kch = self.get_argument("kch")
        time = self.get_argument("time")
        xh = self.get_argument("xh")
        kaoqin = db.bf_kaoqin.find_one({"kch": kch, "time": time}, {"kaoqinjieguo": 1})
        result = kaoqin["kaoqinjieguo"][xh][0]
        self.finish(result)

#最新展示系统

class DXClassesListHandler(BaseRequestHandler):
    @tornado.web.authenticated  
    def get(self):
        user = self.getUser()
        if user[1] != b"m":
        	self.finish("无权限")
        else:
	        db = self.getDB()
	        classes = db.pg_classes.find()
	        eachclass_weeks = []
	        for c in classes:
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
	                    e["average"] = e["points"]/e["nums"]
	                eachclass_week = sorted(eachclass_week, key = lambda x: x["week"])
	            eachclass_weeks.append(eachclass_week)
	        classes = []
	        for c_index, c in enumerate(db.pg_classes.find()):
	            classes.append({"class_int_id": int(c["class_id"]),"class_id": c["class_id"], "class_name": c["class_name"], "ew": eachclass_weeks[c_index]})
	        classes = sorted(classes, key = lambda x: x["class_int_id"]) 
	        self.render('view/dx_classlist.html', user = user, classes = classes, eachclass_weeks = eachclass_weeks, weeks = weeks, dates = dates)

class DXEachClassHandler(BaseRequestHandler):
    @tornado.web.authenticated  
    def get(self):
        user = self.getUser()
        db = self.getDB()
        class_id = self.get_argument("class_id")
        if user[1] == b"t" and user[2] != bytes(class_id, encoding = "utf8"):
        	self.finish("无权限")
        else:
	        c = db.pg_classes.find_one({"class_id": class_id})
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
	                e["average"] = e["points"]/e["nums"]
	            eachclass_week = sorted(eachclass_week, key = lambda x: x["week"])
	        self.render('view/dx_eachclass.html', user = user, classes = c, eachclass_week = eachclass_week, weeks = weeks, dates = dates)

class DXClassesHandler(BaseRequestHandler):
    @tornado.web.authenticated  
    def get(self):
        user = self.getUser()
        db = self.getDB()
        class_id = self.get_argument("class_id")
        if user[1] == b"t" and user[2] != bytes(class_id, encoding = "utf8"):
        	self.finish("无权限")
        else:
            week_num = int(self.get_argument("week"))
            classes = db.pg_classes.find_one({"class_id": class_id}, {"student_faces": 0})
            lesson_nums = classes["lesson_nums"]
            lessons = []
            week_date = ""
            for l in lesson_nums:
                lesson_array = l["lesson_num"].split("_")
                lesson_array = list(map(int, lesson_array))
                lesson_array.append(l["points"])
                if lesson_array[0] == week_num:
                    week_date = l["week_date"]
                    lessons.append(lesson_array[1:])
            lessons = sorted(lessons, key = lambda x: (x[0], x[1]))
            final_lessons = {}
            for l in lessons:
                final_lessons[str(l[0])+"_"+str(l[1])] = l[2]
            if week_num%2 == 0:
                kechengbiao = classes["kechengbiao_dan"]
            else:
                kechengbiao = classes["kechengbiao_shuang"]
            self.render('view/dx_classes.html', user = user, kechengbiao = kechengbiao, classes = classes, lessons = lessons, final_lessons = final_lessons, week_date = week_date, week_num = week_num, weeks = weeks, days = days, classes_nums = classes_nums, classes_names = classes_names)

class DXClassInfoHandler(BaseRequestHandler):
    @tornado.web.authenticated  
    def get(self):
        user = self.getUser()
        db = self.getDB()
        class_id = self.get_argument("class_id")
        if user[1] == b"t" and user[2] != bytes(class_id, encoding = "utf8"):
        	self.finish("无权限")
        else:
            lesson_num = self.get_argument("lesson_num")
            class_info = db.pg_classes.find_one({"class_id": class_id}, {"student_faces": 0})
            students = []
            each_points = []
            week_date = ""
            for s in class_info["students"]:
                students.append(db.pg_students.find_one({"student_id": s, "class_id": class_id}))
                stu_per = db.pg_students_performances.find_one({"StudentID": s,"class_id": class_id, "lesson_num": lesson_num}, projection={"week_date": True, 'points': True, "confirm_faces_states": True})
                week_date = stu_per["week_date"]
                if len(stu_per["confirm_faces_states"]) == 0:
                    each_points.append(101)
                else:
                    each_points.append(stu_per["points"])
            
            self.render('view/dx_ci.html', user = user, each_points = each_points, class_info = class_info, week_date = week_date, students = students, lesson_num = lesson_num, classes_nums = classes_nums, days = days, weeks = weeks)

class DXChangeHandler(BaseRequestHandler):
    @tornado.web.authenticated  
    def get(self):
        user = self.getUser()
        db = self.getDB()
        s = self.get_argument("student_id")
        class_id = self.get_argument("class_id")
        lesson_num = self.get_argument("lesson_num")
        stu_per = db.pg_students_performances.find_one({"StudentID": s,"class_id": class_id, "lesson_num": lesson_num})
        if len(stu_per["confirm_faces"]) > 0:
            old_stu_faces = copy.deepcopy(stu_per["confirm_faces"])
            db.pg_students_performances.update_one({"StudentID": s,"class_id": class_id, "lesson_num": lesson_num}, {"$set": {"confirm_faces": [], "old_confirm_faces": old_stu_faces}})
        else:
            old_stu_faces = copy.deepcopy(stu_per["old_confirm_faces"])
            db.pg_students_performances.update_one({"StudentID": s,"class_id": class_id, "lesson_num": lesson_num}, {"$set": {"confirm_faces": old_stu_faces}})

class DXStudentPerformanceHandler(BaseRequestHandler):
    @tornado.web.authenticated  
    def get(self):
        user = self.getUser()
        db = self.getDB()
        class_id = self.get_argument("class_id")
        if user[1] == b"t" and user[2] != bytes(class_id, encoding = "utf8"):
        	self.finish("无权限")
        else:
            student_id = self.get_argument("student_id")
            lesson_num = self.get_argument("lesson_num")
            class_info = db.pg_classes.find_one({"class_id": class_id}, {"student_faces": 0})
            student = db.pg_students.find_one({"class_id": class_id, "student_id": student_id})
            pics = db.pg_students_performances_imgs.find_one({"StudentID": student_id,"class_id": class_id, "lesson_num": lesson_num})           
            performance = db.pg_students_performances.find_one({"class_id": class_id, "StudentID": student_id, "lesson_num": lesson_num})
            week_date = performance["week_date"]
            performance.update(pics)
            for tp_index,tp in enumerate(performance["timeline_pics"]):
                performance["timeline"][tp_index]["pic"] = tp
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
            if performance["state_array"][6] > 0:
                zhuanzhu = round(float(sa[0] + sa[1] + sa[2] + sa[5])/total_states*100, 2)
                states_pingjia.append(pingjia(zhuanzhu, 85, 60))
                hudong = round(float(sa[2] + sa[5])/total_states*100, 2)
                states_pingjia.append(pingjia(hudong, 5, 1))
                feixuexi = round(float(sa[3] + sa[4])/total_states*100, 2)
                states_pingjia.append(pingjia(feixuexi, 15, 5))
                buqueding = round(float(sa[6])/total_states*100, 2)
                states_pingjia.append(pingjia(buqueding, 15, 5))
            else:
	            zhuanzhu = round(float(sa[0] + sa[1] + sa[2])/total_states*100, 2)
	            states_pingjia.append(pingjia(zhuanzhu, 85, 60))
	            hudong = round(float(sa[2])/total_states*100, 2)
	            states_pingjia.append(pingjia(hudong, 5, 1))
	            feixuexi = round(float(sa[3] + sa[4])/total_states*100, 2)
	            states_pingjia.append(pingjia(feixuexi, 15, 5))
	            buqueding = round(float(sa[5])/total_states*100, 2)
	            states_pingjia.append(pingjia(buqueding, 15, 5))
            self.render('view/dx_student.html', user = user, states_pingjia = states_pingjia, timeline_index = timeline_index, timeline_points = timeline_points, student = student, performance = performance, class_info = class_info, np = np, states = states, week_date = week_date, lesson_num = lesson_num,  classes_nums = classes_nums, days = days, weeks = weeks)

def pingjia(points, maxp, minp):
    if points > maxp:
        return {"point": points, "pingjia": 0}
    elif points > minp:
        return {"point": points, "pingjia": 1}
    else:
        return {"point": points, "pingjia": 2}