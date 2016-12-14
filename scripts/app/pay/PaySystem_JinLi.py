#coding:utf-8
import hmac
import hashlib
import urllib2
import rsa
import time
import datetime
import base64
import json
from app.basehandler import BaseHandler
from app.utils.zlhttpclient import zlHttpClient
from app.utils.views import *

pubkey = rsa.PublicKey.load_pkcs1_openssl_pem('''
    -----BEGIN PUBLIC KEY-----
    MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDV+gtIT6zLR5oglgwqewACyeU0
    x2GLGQ6eyRrGl+qzLVRbXhx/tpQDp6o4Qg4X7g3vpdBMc5RekVj2EG6XcCQI4fx/
    2DA3GYM8X5AypAf4+oI29BS6qgvoWQDEm29E6rgpyvhRzd1V20hHY6wF5DUl+xqU
    9KFUh47F5uWfSjFWtQIDAQAB
    -----END PUBLIC KEY-----
    ''')

privkey = rsa.PrivateKey.load_pkcs1('''
    -----BEGIN RSA PRIVATE KEY-----
    MIICXAIBAAKBgQCBwvcAhoDjnJyw8RcLNCyB2eH6v9fO/jTMBX/BmEbhLYfK96do
    qRnUrsfosnZ/Ws89G3bDPfVbNP6TYwJ8Ioja8NQ/FTu6N2thkqBEycFe73ZRA9dT
    Fs8qQ6yYSorkH0ge9yB5NHGIRZWICa1+jLX+DhDZFYOPTXXsssg6rMDklwIDAQAB
    AoGARQMS6NWgIO2/LB/c2JmT/i+KDxkOxsjN/aADFUxOjh3v9ZOHFpOw6DtYmLqp
    aQw74c0Eecwu/KYPqwViYfDgBX9xLeC751Niy8eaX4R+CWbX2b7/GLjna0Nq7UnM
    wuySvqV2u1QSLq0oC8fwhcyp3FYadcoaKYgaRxqcY4gGgTECQQDyhA2h/uoBEKMM
    vQhxOP/VEvpmh5V+di62i3WL6SoiaFwjSwozP03w9P14S00X1ytcoeb24IPOKlMt
    nwZ3ceqZAkEAiPn6gye4CAmt7aj0XHzIRd3stHDu9XwgN6DTYxRbhILmdITCw+ab
    yPvumH2zeKXoqVGn5a+z2dAebG9d8Bd2rwJAObRmMgef0oUM5vkLyzUO2rpbTo4w
    ahjg4Jqqa5IdbnZ6hgNS+AK2HwGMVlVEkMmoDbCQbmnZsvKrPA280isO8QJADb3+
    mw/uD6hg8boEog7GzPOh3syBvNEyLkKNUqBlOhsj4ca7/4lwUa6s1lGuIsmKWQpf
    LNT+1zhhBQH7S64e8wJBAMfvpOAf8qRrz9aBIJJlECXF43i/t5NCSNXN/eAHBQT+
    7GeMF1yXuCjF+swXuVnKy3o+Naz0qyYyHi8dHsl/0o8=
    -----END RSA PRIVATE KEY-----
    ''')

class HandlerPayJinLi(BaseHandler):
    def post(self):
        cv.log("Got a jinli payment request...", True)
        reqResponse = ""
        parameters = {}
        # 默认参数
        try:
            parameters["api_key"]       = self.get_argument("api_key")
            parameters["close_time"]    = self.get_argument("close_time")
            parameters["create_time"]   = self.get_argument("create_time")
            parameters["deal_price"]    = self.get_argument("deal_price")
            parameters["out_order_no"]  = self.get_argument("out_order_no")
            parameters["pay_channel"]   = self.get_argument("pay_channel")
            parameters["submit_time"]   = self.get_argument("submit_time")
            parameters["user_id"]       = self.get_argument("user_id")
            sign                        = self.get_argument("sign")
        except:
            reqResponse = "FAILURE"
            self.write(reqResponse)
            self.flush()
            self.finish()
            return

        # 拼接原始串
        sortedParams = sorted(parameters.iteritems(), key = lambda d:d[0])
        nativeStr = ""
        for pair in sortedParams:
            nativeStr += "&" + pair[0] + "=" + pair[1]
        nativeStr = nativeStr[1:]
        cv.log("Sign native:%s" % (nativeStr), True)

        mySign = rsa.sign(nativeStr, privkey, 'SHA1')
        cv.log("MySign:%s" % (mySign), True)
        isOk = False
        try:
            isOk = rsa.verify(transdata, sign, pubkey)
        except:
            isOk = False
            cv.log("Verify failed!", True)
        cv.log("result:%s" % isOk, True)
        cv.flush()
        if True: #mySign == sign:
            try:
                url = "http://127.0.0.1:8080/JinLi?deal_price=%s&submit_time=%s&out_order_no=%s&status=%s" %(jTrans["deal_price"], jTrans["submit_time"], jTrans["out_order_no"], isOk)
                request = urllib2.Request(url)
                result = urllib2.urlopen(request).read()
                reqResponse = "SUCCESS"
            except:
                reqResponse = "FAILURE"
        else:
            reqResponse = "FAILURE"
        cv.flush()
        self.write(reqResponse)
        self.flush()
        self.finish()
        