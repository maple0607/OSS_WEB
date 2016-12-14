#coding:utf-8
import time
import json
import datetime
import copy
import urllib
import urllib2
from app.basehandler import BaseHandler
from app.utils.zlhttpclient import zlHttpClient
from tornado.web import authenticated  
from tornado.gen import coroutine
from app.conf.stringtable import *

class Handler_GM_SMS(BaseHandler):
    @authenticated
    def get(self):
        r = self.application.mCfgInfo.mRedisDB
        svrNameById = self.application.mCfgInfo.mServerNameByID
        user = self.get_current_user()  
        self.render("%s/sm_sysmails.html"%(user["op"]), servers = svrNameById)

    @authenticated
    def post(self):
        svrId      = self.get_body_argument("svrid")
        bgntimestr = self.get_body_argument("bgntime")
        endtimestr = self.get_body_argument("endtime")
        plyname    = self.get_body_argument("plyname")
        content    = self.get_body_argument("content")
        startTime  = time.mktime(time.strptime(bgntimestr, "%Y-%m-%d %H:%M"))
        endTime    = time.mktime(time.strptime(endtimestr, "%Y-%m-%d %H:%M"))  
        sendData   = {"Action":29, "ServerID":int(svrId),"Name":plyname,  "StartTime":startTime, "StopTime":endTime, "Content":content} 
        httpClient = zlHttpClient()  
        rsltData   = httpClient.sendToGM(sendData)
        jdata = json.loads(rsltData)
        dataInfo = json.loads(jdata["data"])
        result = ""
        if len(dataInfo) > 0:
            result += "<table class='table'><thead><tr><th>发送时间</th><th>收件人</th><th>邮件类容</th></tr></thead><tbody>"
            for data in dataInfo:
                sendTime = data["sendTime"]
                recverName = data["recvName"]
                mailbody = data["mailBody"]
                result += "<tr><td>%s</td><td>%s</td><td>%s</td></tr>" %(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(sendTime))), recverName, mailbody)
            result+="</tbody></table>"

        else:
            result = "尚未查询到数据"
        self.write(result)
        self.flush()
        self.finish()                
