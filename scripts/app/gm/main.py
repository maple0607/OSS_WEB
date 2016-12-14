#coding:utf-8
import time
from tornado.web import authenticated 
from app.basehandler import BaseHandler
from tornado.gen import coroutine
from traceback import print_exc

class Handler_Index(BaseHandler):
    @authenticated
    @coroutine
    def get(self):
       board = self.application.mCfgInfo.mLoginBoard
       svrNameById = self.application.mCfgInfo.mServerNameByID
       svrs = self.searchServerInfo()
       svrStatus = []
       for svrID in svrNameById:
            if str(svrID) in svrs:
                data = svrs[str(svrID)]
                MoneyNum = -1
                try:
                    db = self.application.mCfgInfo.mPayDB
                    sqlstr = "select sum(Money) from unhandled where ServerID = %s" % (svrID)
                    cur = yield db.execute(sqlstr)
                    res = cur.fetchall()
                    MoneyNum = res[0][0]
                except:
                    print_exc()
                svrStatus.append((svrID, svrNameById[svrID], data[1], data[2], data[3], data[4], MoneyNum))
            else:
                svrStatus.append((svrID, svrNameById[svrID], 0, 0, 0, 0, -1))
       '''for svrID in svrs:
            data = svrs[svrID]
            if int(svrID) not in svrNameById:
                svrStatus.append((svrID, "Unknown", data[1], data[2], data[3], data[4], data[5]))'''

       user = self.get_current_user()
       self.render("%s/index.html"%(user["op"]), loginBoard=board, svrgroup= svrStatus)

    def searchServerInfo(self):
        r = self.application.mCfgInfo.mRedisDB
        curTime = time.time()
        day = time.strftime('%Y%m%d')
        svrs = r.smembers(day)
        statusInfo = {}
        for svr in svrs:
            actNum = r.scard("%s:%s:act" % (day, svr))
            actNum if actNum else 0
            maxol  = r.get("%s:%s:max" % (day, svr))
            if maxol == None:
                maxol = 0
            curol  = r.get("%s:%s:cur" % (day, svr))
            curol if curol else 0
            svrTime = r.hget("game:%s" % (svr), "updatetime")
            svrTime if svrTime else 0
            gstatus = 0
            if int(curTime) - int(svrTime) <= 60:
                gstatus = 1
            bstatus = -1
            bsVals = r.hmget("bs:state:%s" % (svr), "update", "cur")
            if bsVals[0] != None and bsVals[1] != None:
                if int(curTime) - int(bsVals[0]) < 20:
                    bstatus = bsVals[1]
            statusInfo[svr] = [svr, curol, maxol, actNum, gstatus, bstatus]
        return statusInfo  

    def caluChargeData(self):
        #db = self.application.mCfgInfo.
        pass