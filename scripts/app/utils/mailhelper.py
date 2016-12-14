#coding=utf8

import tornado.web
import tornado.gen
import tornado.httpserver
import tornado.web
import tornado.ioloop
import tornado.options
import urllib
import urllib2
import time
import os
import sys
import json
import base64
import hashlib

reload(sys)
sys.setdefaultencoding('utf-8')

class MailHelper:
    def __init__(self):
        self.mKey = "yinwuweiye"
        self.mGMUrl = "http://127.0.0.1:8081/?sign="

    def sendmail(self, svr, name, desc, rewards):
        items = ""
        res = ""
        for reward in rewards:
            if len(reward) == 2:
                rewardStr = "%s,%s;" % (reward[0], reward[1])
                res += rewardStr
            elif len(reward) == 3:
                rewardStr = "%s,%s,%s;" % (reward[0], reward[1], reward[2])
                items += rewardStr

        curTime = time.time()
        data = {}
        data["Action"]      = 8
        data["ServerID"]    = int(svr)
        data["Name"]        = name
        data["Flag"]        = 0
        data["Mail"]        = desc
        data["Items"]       = items
        data["Res"]         = res
        data["SendTime"]    = curTime
        data["VlidTime"]    = int(curTime) + 86400 * 3
        
        jsonData = json.dumps(data, sort_keys=True)
        encodedData = base64.b64encode(jsonData)
        sign = hashlib.sha1(encodedData + self.mKey).hexdigest()

        alldata = {}
        alldata["data"]     = jsonData
        alldata["sign"]     = sign

        jsonDataAll = json.dumps(alldata, sort_keys=True)

        url = "%s%s" % (self.mGMUrl, sign)
        try:
            request = urllib2.Request(url)
            request.add_data(jsonDataAll)
            response = urllib2.urlopen(request, timeout=10)
            resdata = response.read()
            return True
        except:
            return False