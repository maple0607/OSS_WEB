#coding:utf-8

import threading
import hmac
import hashlib
import urllib2
import time
import datetime
import json
from app.basehandler import BaseHandler
from app.utils.zlhttpclient import zlHttpClient
from tornado.gen import coroutine

gSecretKey = "7e512394a04fb86de1d1c946e109b1f7"

class HandlerPaySY185(BaseHandler):
    @coroutine
    def get(self):
        # self.mPaySy185 = PaySy185()
        # self.mPaySy185.start()
        result={}
        f = True
        try:
            vip=int(self.get_argument("vip"))
            account=self.get_argument("account")
            playerName=self.get_argument("playerName")
            playerId=self.get_argument("playerId")
            value=int(self.get_argument("value"))
            serverid=int(self.get_argument("serverid"))
            orderno=self.get_argument("orderno")
            sign=self.get_argument("sign")
            account = "sy185_" + account
        except:
            f = False
            result["errorcode"] = 1
            result["msg"] = "param error"
        if f:
            m=hashlib.md5()
            m.update(str(account)+"#"+str(value)+"#"+str(serverid)+"#"+gSecretKey)
            mysign=m.hexdigest()
            sendData = {"Action":1, "ServerID":serverid, "Name":playerName}
            httpClient = zlHttpClient()
            resultData = httpClient.sendToGM(sendData)
            jdata = json.loads(resultData)
            noticeJsonArry = json.loads(jdata["data"])
            resultInfo = {}
            flag = True
            try:
                info = noticeJsonArry[0]
                resultInfo["account"] = info["Account"]
            except:
                flag = False
                result["errorcode"] = 3
                result["msg"] = "no player"
            if flag:
                if account == resultInfo["account"]:
                    if mysign == sign:
                        db = self.application.mCfgInfo.mGMDB
                        sqlstr = "select * from Reissue where OrderNo = '%s' UNION select * from Reissued where OrderNo = '%s'" % (orderno, orderno)
                        cur = yield db.execute(sqlstr)
                        row = cur.fetchall()
                        if len(row) == 0:
                            sqlstr = "insert into Reissue values(NULL,'%s','%s','%s',%s,'%s',%s,%s,%s);" % (orderno, account, playerId, serverid, playerName, value, vip, 0)
                            cur = yield db.execute(sqlstr)
                            result["errcode"] = 0
                            result["msg"] = "succeed"
                        else:
                            result["errcode"] = 4
                            result["msg"] = "orderno error"
                    else:
                        result["errcode"] = 2
                        result["msg"] = "failded"
                else:
                    result["errorcode"] = 1
                    result["msg"] = "param error"    
        data = json.dumps(result)
        self.write(data)
        self.flush()
        self.finish()
