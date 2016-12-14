#coding:utf-8
import hmac
import hashlib
import urllib2
import rsa
import time
import datetime
import base64
from app.basehandler import BaseHandler
from app.utils.zlhttpclient import zlHttpClient
from app.utils.views import *

pubkey = rsa.PublicKey.load_pkcs1_openssl_pem('''
    -----BEGIN PUBLIC KEY-----
    MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCmreYIkPwVovKR8rLHWlFVw7YD
    fm9uQOJKL89Smt6ypXGVdrAKKl0wNYc3/jecAoPi2ylChfa2iRu5gunJyNmpWZzl
    CNRIau55fxGW0XEu553IiprOZcaw5OuYGlf60ga8QT6qToP0/dpiL/ZbmNUO9kUh
    osIjEu22uFgR+5cYyQIDAQAB
    -----END PUBLIC KEY-----
    ''')

class HandlerPayHuaWei(BaseHandler):
    def get(self):
        cv.log("Got a huawei payment request...", True)
        reqResponse = ""
        parameters = {}
        # 默认参数
        try:
            parameters["result"]      = self.get_argument("result")
            parameters["userName"]    = self.get_argument("userName")
            parameters["productName"] = self.get_argument("productName")
            parameters["payType"]     = self.get_argument("payType")
            parameters["amount"]      = self.get_argument("amount")
            parameters["orderId"]     = self.get_argument("orderId")
            parameters["notifyTime"]  = self.get_argument("notifyTime")
            parameters["requestId"]   = self.get_argument("requestId")
            sign                      = self.get_argument("sign")
        except:
            reqResponse = "{ \"result\" : 98 }"
            self.write(reqResponse)
            self.flush()
            self.finish()
            return

        if int(parameters["result"]) != 0:
            reqResponse = "{ \"result\" : 99 }"
            self.write(reqResponse)
            self.flush()
            self.finish()
            return

        # 可变参数
        self.checkSelectableParam(parameters, "bankId")
        self.checkSelectableParam(parameters, "orderTime")
        self.checkSelectableParam(parameters, "tradeTime")
        self.checkSelectableParam(parameters, "accessMode")
        self.checkSelectableParam(parameters, "spending")
        self.checkSelectableParam(parameters, "extReserved")
        self.checkSelectableParam(parameters, "sysReserved")

        # 拼接原始串
        sortedParams = sorted(parameters.iteritems(), key = lambda d:d[0])
        nativeStr = ""
        for pair in sortedParams:
            nativeStr += "&" + pair[0] + "=" + pair[1]
        nativeStr = nativeStr[1:]
        # 签名方式
        try:
            signType = self.get_argument("signType")
        except:
            signType = "RSA"
        cv.log("Native string:%s" % nativeStr, True)
        cv.log("Sign:%s" % sign, True)
        signNative = base64.decodestring(sign)
        cv.log("Sign native:%s" % signNative, True)
        try:
            isOk = rsa.verify(nativeStr, signNative, pubkey)
        except:
            isOk = False
        cv.log("result:%s" % isOk, True)
        if True: #mySign == sign:
            url = "http://127.0.0.1:8080/huawei?amount=%s&orderId=%s&productName=%s&notifyTime=%s&requestId=%s&status=%s" %(parameters["amount"], parameters["orderId"], parameters["productName"], parameters["notifyTime"], parameters["requestId"], isOk)
            request = urllib2.Request(url)
            result = urllib2.urlopen(request).read()
            reqResponse = "{ \"result\" : 0 }"
        else:
            reqResponse = "{ \"result\" : 1 }"

        self.write(reqResponse)
        self.flush()
        self.finish()
    def post(self):
        cv.log("Got a huawei payment request...", True)
        reqResponse = ""
        parameters = {}
        # 默认参数
        try:
            parameters["result"]      = self.get_argument("result")
            parameters["userName"]    = self.get_argument("userName")
            parameters["productName"] = self.get_argument("productName")
            parameters["payType"]     = self.get_argument("payType")
            parameters["amount"]      = self.get_argument("amount")
            parameters["orderId"]     = self.get_argument("orderId")
            parameters["notifyTime"]  = self.get_argument("notifyTime")
            parameters["requestId"]   = self.get_argument("requestId")
            sign                      = self.get_argument("sign")
        except:
            reqResponse = "{ \"result\" : 98 }"
            self.write(reqResponse)
            self.flush()
            self.finish()
            return

        if int(parameters["result"]) != 0:
            reqResponse = "{ \"result\" : 99 }"
            self.write(reqResponse)
            self.flush()
            self.finish()
            return

        # 可变参数
        self.checkSelectableParam(parameters, "bankId")
        self.checkSelectableParam(parameters, "orderTime")
        self.checkSelectableParam(parameters, "tradeTime")
        self.checkSelectableParam(parameters, "accessMode")
        self.checkSelectableParam(parameters, "spending")
        self.checkSelectableParam(parameters, "extReserved")
        self.checkSelectableParam(parameters, "sysReserved")

        # 拼接原始串
        sortedParams = sorted(parameters.iteritems(), key = lambda d:d[0])
        nativeStr = ""
        for pair in sortedParams:
            nativeStr += "&" + pair[0] + "=" + pair[1]
        nativeStr = nativeStr[1:]
        # 签名方式
        try:
            signType = self.get_argument("signType")
        except:
            signType = "RSA"
        cv.log("Native string:%s" % nativeStr, True)
        cv.log("Sign:%s" % sign, True)
        signNative = base64.decodestring(sign)
        cv.log("Sign native:%s" % signNative, True)
        try:
            isOk = rsa.verify(nativeStr, signNative, pubkey)
        except:
            isOk = False
        cv.log("result:%s" % isOk, True)
        if True: #mySign == sign:
            url = "http://127.0.0.1:8080/huawei?amount=%s&orderId=%s&productName=%s&notifyTime=%s&requestId=%s&status=%s" %(parameters["amount"], parameters["orderId"], parameters["productName"], parameters["notifyTime"], parameters["requestId"], isOk)
            request = urllib2.Request(url)
            result = urllib2.urlopen(request).read()
            reqResponse = "{ \"result\" : 0 }"
        else:
            reqResponse = "{ \"result\" : 1 }"

        self.write(reqResponse)
        self.flush()
        self.finish()

    def checkSelectableParam(self, paramsDict, paramName):
        try:
            paramsDict[paramName] = self.get_argument(paramName)
            return True
        except:
            return False
        