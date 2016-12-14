#coding:utf-8

import threading
import hmac
import hashlib
import urllib
import urllib2
import time
import datetime
import json
from app.basehandler import BaseHandler
from app.utils.zlhttpclient import zlHttpClient
from traceback import print_exc
CPID ="20151210165856312833"
APPID ="e10eb985f85c331ad4ee4de75e3c7427"
NOTIFYURL = "http://182.254.156.106:8080/Vivo"
CPKEY = "164cfe5005f1de301e1bc858b3568558"

class HandlerPayVivoTrade(BaseHandler):
    def get(self):
        productid = self.get_argument("productid")
        price = self.get_argument("price")
        goldmoney = self.get_argument("goldmoney")
        orderSerial = self.get_argument("cporder")
        result = self.postModifyOrderSerial(productid, price, goldmoney, orderSerial)
        self.write(result)
        self.flush()
        self.finish()

    def postModifyOrderSerial(self, productid, price, goldmoney, orderSerial):
        curTime = time.localtime()
        params = { 
            "version": "1.0.0",
            "signMethod": "MD5", 
            "signature":"",
            "cpId": CPID, 
            "appId": APPID, 
            "cpOrderNumber": str(orderSerial),
            "notifyUrl": str(NOTIFYURL),
            "orderTime": "%04d%02d%02d%02d%02d%02d" % ( curTime.tm_year, curTime.tm_mon, curTime.tm_mday, curTime.tm_hour, curTime.tm_min, curTime.tm_sec),
            "orderAmount": int(price),
            "orderTitle": str("%s" % (goldmoney)),
            "orderDesc": str("%s" % (goldmoney)),
            "extInfo": str(productid),
        }
        tempsign = "appId=%s&cpId=%s&cpOrderNumber=%s&extInfo=%s&notifyUrl=%s&orderAmount=%d&orderDesc=%s&orderTime=%s&orderTitle=%s&version=%s&%s" % (
            params["appId"],
            params["cpId"],
            params["cpOrderNumber"],
            params["extInfo"],
            params["notifyUrl"],
            params["orderAmount"],
            params["orderDesc"],
            params["orderTime"],
            params["orderTitle"],
            params["version"],
            (hashlib.md5(CPKEY).hexdigest()).lower())
        params["signature"] = hashlib.md5(tempsign).hexdigest()
        try:
            rep = urllib2.urlopen("https://pay.vivo.com.cn/vcoin/trade", urllib.urlencode(params)).read()
            data = json.loads(rep)
            
            print data
            if data["respCode"] == "200":
                signStr = "accessKey=%s&orderAmount=%s&orderNumber=%s&respCode=%s&respMsg=%s&%s" % (
                    data["accessKey"],
                    data["orderAmount"],
                    data["orderNumber"],
                    data["respCode"],
                    data["respMsg"],
                    (hashlib.md5(CPKEY).hexdigest()).lower())
                sign = hashlib.md5(signStr).hexdigest()

                if sign == data["signature"]:
                    result = "%s:%s:%s:%s" % (
                        data["accessKey"],
                        data["orderNumber"],
                        data["orderAmount"],
                        orderSerial)
                    return result
        except:
            print_exc()
            return ""
