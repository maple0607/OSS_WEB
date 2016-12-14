#coding=utf8

import tornado.web
import tornado.gen
import tornado.httpserver
import tornado.web
import tornado.ioloop
import tornado.options
import redis
import time
import os
import hashlib
import urllib2
import json
import random
import traceback
from app.basehandler import BaseHandler
from app.utils.zlhttpclient import zlHttpClient


class Handler_PlayerCreate(BaseHandler):
    @tornado.gen.coroutine
    def get(self):
        self.application.checkPermission(self)
        r = self.application.mCfgInfo.mRedisDB

        try:
            svr = self.get_argument("s")
            udid = self.get_argument("u")
            accType = self.get_argument("t")
            acc = self.get_argument("a")
            level = self.get_argument("l")
            name = self.get_argument("n")
            createTime = self.get_argument("ct")
            curTime = int(time.time())

            ##log create
            try:
                db = self.application.mCfgInfo.mWebDB
                sqlstr = "call insertCreate('%s', '%s', %s, %s, %s);" % (acc, udid, svr, accType, curTime)
                cur = yield db.execute(sqlstr)
            except:
                traceback.print_exc()
            ##log end

            ##ios ad for cmge API
            if int(accType) == 34:
                sourcestr = "gfsl&&%s&1016751149&b99802100ef78b519f986ad3c7de0ebc" % (udid)
                m = hashlib.md5()
                m.update(sourcestr)
                sign = m.hexdigest()
                url = "http://syhz.cmge.com/cp/cpud?account=gfsl&mac=&idfa=%s&appId=1016751149&ip=&actionTime=%s&sign=%s" % (udid, curTime, sign)
                #print url
                request = urllib2.Request(url)
                response = urllib2.urlopen(request, timeout=5).read()
                #print response
            ##ios ad end
            self.write("")
            self.flush()
            self.finish()
        except:
            traceback.print_exc()

class Handler_PlayerOnLine(BaseHandler):
    @tornado.gen.coroutine
    def get(self):
        self.application.checkPermission(self)

        r = self.application.mCfgInfo.mRedisDB
        try:
            svr = self.get_argument("s")
            udid = self.get_argument("u")
            accType = self.get_argument("t")
            acc = self.get_argument("a")
            level = self.get_argument("l")
            viplevel = self.get_argument("vl")
            name = self.get_argument("n")
            createTime = self.get_argument("ct")
            curTime = int(time.time())
            #self.AddOrder(acc,svr)

            ##log active
            try:
                db = self.application.mCfgInfo.mWebDB
                sqlstr = "call insertActive('%s', '%s', %s, %s, %s, %s, %s, %s);" % (acc, udid, svr, accType, createTime, curTime, level, viplevel)
                cur = yield db.execute(sqlstr)
            except:
                traceback.print_exc()
            ##log end

            day = time.strftime('%Y%m%d')
            daySvr = "%s:%s:act" % (day, svr)
            r.sadd(day, svr)
            r.sadd(daySvr, acc)

            sKeyName = "svr:pinfo"
            sPName = "%s:%s" % (svr, name)
            pinfo = {"n": name, "l": level, "lt": curTime, "ct": createTime}
            pinfostr = json.dumps(pinfo)
            r.hset(sKeyName, sPName, pinfostr)

            if int(accType) == 21:
                accstr = acc.split("_")
                if len(accstr) == 2:
                    openid = accstr[1]
                    r.hset("tx:openid:%s" % (openid), "%s" % (svr), pinfostr)

            keyName = "svr:players"
            r.sadd(keyName, udid)

            accTypeHeader = "acc:type"
            keyAccTypeName = "acc:type:%s" % (accType)
            r.sadd(accTypeHeader, accType)
            r.sadd(keyAccTypeName, acc)

            udidTypeHeader = "udid:type"
            keyUdidType = "udid:type:%s" % (accType)
            r.sadd(udidTypeHeader, accType)
            r.sadd(keyUdidType, udid)

            self.write("")
            self.flush()
            self.finish()
        except:
            traceback.print_exc()

    # @tornado.gen.coroutine
    # def AddOrder(self, acc = "", svr = -1):
    #     httpClient = zlHttpClient()
    #     if acc != "" or svr != -1:
    #         db = self.application.mCfgInfo.mGMDB
    #         sqlstr = "select * from Reissue where Account = '%s' and ServerID = %s;" % (acc,svr)
    #         cur = yield db.execute(sqlstr)
    #         while (True):
    #             row = cur.fetchone()
    #             if row != None:
    #                 orderno = row[1]
    #                 account = row[2]
    #                 UUID = row[3]
    #                 serverId = row[4]
    #                 name = row[5]
    #                 addGold = int(row[6])
    #                 vip = int(row[7])
    #                 sendData = {"Action":27, "ServerID":serverId, "addGold":addGold,"vip":vip}
    #                 resultData = httpClient.sendToGM(sendData)
    #                 jdata = json.loads(resultData)
    #                 errcode = int(jdata["errorCode"])
    #                 if errcode == 0:
    #                     sqlstr = "delete from Reissue where Account = '%s' and ServerID = %s and OrderNo = '%s';" % (acc,svr,orderno)
    #                     yield db.execute(sqlstr)
    #                     sqlstr = "insert into Reissued values(NULL,'%s','%s','%s',%s,'%s',%s,%s,%s);" % (orderno, account, UUID, serverId, name, addGold, vip, 1)
    #                     yield db.execute(sqlstr)
    #             else:
    #                 break

class Handler_Player_Info(BaseHandler):
    def get(self):
        r = self.application.mCfgInfo.mRedisDB

        valid = False
        info = {}

        try:
            svr = self.get_argument("s")
            name = self.get_argument("n")

            sKeyName = "svr:pinfo"
            sPName = "%s:%s" % (svr, name)
            jspinfo = r.hget(sKeyName, sPName)
            if jspinfo != None:
                pinfo = json.loads(jspinfo)
                valid = True
                info["Svr"] = svr
                info["Name"] = name
                info["Level"] = pinfo["l"]
                info["LoginTime"] = pinfo["lt"]
        except:
            traceback.print_exc()

        self.write(json.dumps({"Valid": valid, "Info": info}))
        self.flush()
        self.finish()