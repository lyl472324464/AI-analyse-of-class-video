#!/usr/bin/python
# -*- coding: UTF-8 -*-

from app import base, account, view, api, warning, xcx
from app import test

handlers=[
    (r'/', base.IndexHandler),    
    
    # 账户系统          
    (r'/signin', account.SignInHandler),  
    (r'/signup', account.SignUpHandler), 
    (r'/signout', account.SignOutHandler),
    (r'/myaccount', account.MyAccountHandler), 
    (r'/advise', account.AdviseHandler), 
    (r'/cp', account.ChangePasswordHandler), 
    
    # 预警系统
    (r'/warning', warning.WarningIndexHandler),
    (r'/wcd', warning.ClassDetailHandler),
    (r'/faster', warning.FasterHandler),
    (r'/getfaster', warning.GetFasterHandler),
    (r'/startanalyse', warning.StartAnalyseHandler),
    (r'/stopanalyse', warning.StopAnalyseHandler),

    # 学生角色                  
    (r'/sl', view.StudentEachLessonPerformanceHandler),
    (r'/sw', view.StudentEachWeekPerformanceHandler),
    (r'/swc', view.StudentEachWeekEachKindClassPerformanceHandler),
    (r'/gsp', view.GetStudentTimelinePicHandler),

    # 课堂角色
    (r'/cw', view.ClassInfoEachWeekHandler),
    (r'/cl', view.ClassInfoEachLessonHandler), 
    (r'/cwc', view.ClassInfoEachWeekEachKindClassHandler), 

    # 学校
    (r'/xz', view.XZHandler),
    (r'/si', view.SchoolInfoHandler),
    (r'/sic', view.SchoolInfoEachKindClassHandler),

    # 年级
    (r'/gi', view.GradeInfoHandler),

    # 北服
    (r'/bf', view.ClassInfoBFHandler), 
    (r'/bfs', view.StudentBFHandler), 
    (r'/kq', view.KaoQinBF),
    (r'/kqimg', view.GetKaoQinImgBF),
    
    #大兴
    (r'/dxclasseslist', view.DXClassesListHandler),
    (r'/dxeachclass', view.DXEachClassHandler),
    (r'/dxclasses', view.DXClassesHandler),
    (r'/dxci', view.DXClassInfoHandler),
    (r'/dxs', view.DXStudentPerformanceHandler),
    (r'/dxchange', view.DXChangeHandler),
    # 小程序API接口
    (r'/xcxclasslist', xcx.XcxClassesListHandler),
    (r'/xcxclassreportlist', xcx.XcxClassReportlistHandler),
    (r'/xcxclassreportdetail',xcx.XcxClassReportdetailHandler),
    (r'/xcxeachlessonreport',xcx.XcxEachLessonReportHandler),
    (r'/xcxstudenteachlessonreport',xcx.XcxStudentEachLessonReportHandler),
    (r'/xcxsearch',xcx.XcxSearchHandler),
    
    
    # 测试专用    

    # 404  
    (r'.*', base.ErrorHandler),        
]