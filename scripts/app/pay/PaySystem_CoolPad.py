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

class HandlerPayCoolPad(BaseHandler):
    def post(self):
        cv.log("Got a coolpad payment request...", True)
        reqResponse = ""
        parameters = {}
        # 默认参数
        try:
            transdata = self.get_argument("transdata")
            cv.log("trans:%s" % (transdata), True)
            sign      = self.get_argument("sign")
            cv.log("sign:%s" % (sign), True)
            signtype  = self.get_argument("signtype")
            cv.log("signtype:%s" % (signtype), True)
        except:
            reqResponse = "FAILURE"
            self.write(reqResponse)
            self.flush()
            self.finish()
            return

        mySign = rsa.sign(transdata, privkey, 'MD5')
        #cv.log("MySign:%s" % (mySign), True)
        isOk = False
        try:
            isOk = rsa.verify(transdata, sign, pubkey)
        except:
            isOk = False
            cv.log("Verify failed!", True)
        cv.log("result:%s" % isOk, True)
        cv.flush()
        if True: #mySign == sign:
            jTrans = json.loads(transdata)
            try:
                url = "http://127.0.0.1:8080/coolpad?money=%s&transid=%s&waresid=%s&transtime=%s&cporderid=%s&status=%s" %(jTrans["money"], jTrans["transid"], jTrans["waresid"], int(time.time()), jTrans["cporderid"], isOk)
                cv.log("Request url:%s" % url, True)
                request = urllib2.Request(url)
                result = urllib2.urlopen(request).read()
                reqResponse = "SUCCESS"
                cv.log("Pay finished!", True)
            except:
                reqResponse = "FAILURE"
        else:
            reqResponse = "FAILURE"
        cv.flush()
        self.write(reqResponse)
        self.flush()
        self.finish()
        