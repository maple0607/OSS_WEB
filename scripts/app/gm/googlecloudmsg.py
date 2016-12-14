#coding:utf-8
import time
import json
import datetime
import copy
import urllib
import urllib2
from app.basehandler import *
from app.utils.zlhttpclient import zlHttpClient
from tornado.web import authenticated  
from tornado.gen import coroutine
from app.conf.stringtable import *


class Handler_GM_GCM(BaseHandler):
    @authenticated
    @coroutine
    def get(self):
        r = self.application.mCfgInfo.mRedisDB
        maxDevices = r.scard("Client_RegisterID")
        msglen = r.llen("goolecloudmsg")
        data = r.lrange("goolecloudmsg", 0, msglen)
        user = self.get_current_user()
        opdata = yield self.getGMLog(GMOP_AddGCMMessage)
        record = self.convertToString(opdata)
        self.render("%s/cloud_message.html"%(user["op"]), maxDevices = maxDevices, msg = data, record = record)

    @authenticated
    def post(self):
        r        = self.application.mCfgInfo.mRedisDB
        sendTime = self.get_body_argument("stime")
        cmsg     = self.get_body_argument("message")
        data = "%s|%s" %(sendTime, cmsg)
        r.rpush("goolecloudmsg", data)
        self.gmLog(GMOP_AddGCMMessage, "[Time:%s; Message:%s]" %(sendTime, cmsg))
        self.write("1")
        self.flush()
        self.finish()


    def convertToString(self, recordData):
        lines = []
        for rd in recordData:
            lines.append("[%s][%s]======>%s" %(rd[1], time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(rd[2])), rd[4]))
        return lines

