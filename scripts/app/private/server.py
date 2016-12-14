#coding=utf8
import time
import os
import json
import traceback
from app.conf import *

from app.basehandler import BaseHandler
Server_State_Good       = 1
Server_State_Busy       = 2
Server_State_Hot        = 3
Server_State_New        = 4
Server_State_Recommend  = 5

sLastRefreshTime = int(time.time())

class Handler_Game_Status(BaseHandler):
    def get(self):
        r = self.application.mCfgInfo.mRedisDB
        svr = self.get_argument("svrid")
        serverName = self.get_argument("svrname")
        httpIP = self.get_argument("httpip")
        httpPort = self.get_argument("httpport")
        curPlayers = self.get_argument("curplayers")
        maxPlayers = self.get_argument("maxplayers")
        curol = self.get_argument("curonline")
        updateTime = int(time.time())
        day = time.strftime('%Y%m%d')
        daySvrMaxOL = "%s:%s:max" % (day, svr)
        daySvrCurOL = "%s:%s:cur" % (day, svr)
        SvrMaxOL = "%s:max" %(svr)
        #每半个小时记录一次在线人数
        t = time.localtime(updateTime)
        updateMTime = t.tm_min + t.tm_hour * 60
        #if updateMTime % 30 == 0 and t.tm_sec <= 10:
        daySvrOLInfo = "%s:%s" %(day, svr)
        value = "%s:%s,%s" %(t.tm_hour,t.tm_min, curol)
        r.sadd(daySvrOLInfo, value)
        r.sadd(day, svr)
        r.set(daySvrCurOL, curol)
        maxol = r.get(daySvrMaxOL)
        if maxol == None:
            maxol = 0
        else:
            maxol = int(maxol)

        curol = int(curol)
        if curol > maxol:
            r.set(daySvrMaxOL, curol)

        #历史最高在线
        hvalue = r.get(SvrMaxOL)
        hmaxol = 0
        curTime = time.strftime("%Y-%m-%d %H:%M:%S")
        if hvalue == None:
            value = "%s|%s" %(curol, curTime)
            r.set(SvrMaxOL,value)
        else:
            listData = hvalue.split("|")
            hmaxol = int(listData[0])
            if curol > hmaxol:
                value = "%s|%s" %(curol, curTime)
                r.set(SvrMaxOL,value)

        data = {}
        data["id"] = svr
        data["name"] = serverName
        data["http:ip"] = httpIP
        data["http:port"] = httpPort
        data["curplayers"] = curPlayers
        data["maxplayers"] = maxPlayers
        data["updatetime"] = updateTime

        p = r.pipeline()
        p.hmset("game:%s" % (svr), data)
        p.sadd("game:ids", svr)
        ret = p.execute()
        global sLastRefreshTime
        if updateTime - sLastRefreshTime > 300:
            sLastRefreshTime = updateTime
            conf.Instance.updateServerList()

        self.write(str(ret))
        self.flush()
        self.finish()

class Handler_Battle_Status(BaseHandler):
    def get(self):
        r = self.application.mCfgInfo.mRedisDB
        svr = self.get_argument("svrid")
        curPlayers = self.get_argument("curplayers")
        updateTime = int(time.time())
        key = "bs:state:%s" % (svr)
        r.hmset(key, {"update" : updateTime, "cur" : curPlayers})
        self.write("1")
        self.flush()
        self.finish()

class Handler_Connector_Status(BaseHandler):
    def get(self):
        self.application.checkPermission(self)

        r = self.application.mCfgInfo.mRedisDB

        svr = self.get_argument("svrid")
        serverIP = self.get_argument("svrip")
        serverPort = self.get_argument("svrport")
        curClients = self.get_argument("curclients")
        maxClients = self.get_argument("maxclients")
        updateTime = int(time.time())
        
        connectorID = "%s:%s" % (serverIP, serverPort)

        data = {}
        data["id"] = connectorID
        data["svrip"] = serverIP
        data["svrport"] = serverPort
        data["curclients"] = curClients
        data["maxclients"] = maxClients
        
        p = r.pipeline()
        p.hmset("game:%s:connector:%s" % (svr, connectorID), data)
        p.expire("game:%s:connector:%s" % (svr, connectorID), 12)
        p.sadd("game:%s:connectors" % (svr), connectorID)
        ret = p.execute()

        self.write(str(ret))
        self.flush()
        self.finish()
