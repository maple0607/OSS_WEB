#coding=utf8
import json
import time
from tornado.gen import coroutine
from tornado.gen import Return
from tornado.web import RequestHandler
from tornado.web import ErrorHandler
from tornado.web import HTTPError
from traceback import print_exc
GMOP_Login              = 0
GMOP_OpenServer         = 1
GMOP_CloseServer        = 2
GMOP_DeleteServer       = 3
GMOP_ModifyBanner       = 4
GMOP_AddAnnouncement    = 5
GMOP_ModifyAnnouncement = 6
GMOP_DeleteAnnouncement = 7
GMOP_ResendHttpQueue    = 8
GMOP_SetVersion         = 9
GMOP_SaveGiftPack       = 10
GMOP_SendMail           = 11
GMOP_AddUser            = 12
GMOP_DelUser            = 13
GMOP_ModifyUser         = 14
GMOP_SendRollingAnnouce = 15
GMOP_DeleteRollingAnnouce = 16
GMOP_AddGCMMessage      = 17
GMOP_Names = [
    "Login",
    "OpenServer",
    "CloseServer",
    "DeleteServer",
    "ModifyBanner",
    "AddAnnouncement",
    "ModifyAnnouncement",
    "DeleteAnnouncement",
    "ResendHttpQueue",
    "SetVersion",
    "SaveGiftPack",
    "SendMail",
    "AddUser",
    "DelUser",
    "ModifyUser",
    "SendRollingAnnouce",
    "AddGCMMessage",
 ]
def getGMOPName(opType):
    num = len(GMOP_Names)
    if opType >= 0 and opType < num:
        return GMOP_Names[opType]
    else:
        return "Unknown"
     
class BaseHandler(RequestHandler):
    def get_current_user(self):
        r = self.application.mCfgInfo.mRedisDB
        key = self.get_secure_cookie("user")
        userParam = [
            "name",
            "op",
        ]
        userData = r.hmget("user:%s" % (key), userParam)

        user = {}
        for i in xrange(len(userParam)):
            user[userParam[i]] = userData[i]

        if user["op"] == None:
            user["op"] = 0
        else:
            user["op"] = int(user["op"])
        if user["name"] == None:
            return None
        else:
            r.expire("user:%s" % (key), 3600)
            return user

             
    @coroutine
    def gmLog(self, opType, opData):
        user = self.get_current_user()
        db = self.application.mCfgInfo.mGMDB
        username = ""
        if user:
            username = user["name"]
        try:
            yield db.execute("insert into `GMOperationLog` (`Username`, `opTime`, `opType`, `opData`) values ('%s', %s, %s, '%s');" % (
                username,
                int(time.time()),
                opType,
                opData))
        except:
            print_exc()

    @coroutine
    def getGMLog(self, opType):
        user = self.get_current_user()
        db = self.application.mCfgInfo.mGMDB
        username = ""
        if user:
            username = user["name"]
            cur = yield db.execute("SELECT * FROM `GMOperationLog` WHERE Username = '%s' AND opType = %s ORDER BY opTime DESC;" % (username, opType))
            result = cur.fetchall()
            raise Return(result)


