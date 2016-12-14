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
    MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAlBgkYQNptrGL065RC5Oh
    08rIKL9kDbQHR0sRAqm3llRH1Y5KZuIPT30nj7JEFLdi1Wn0Ves2JJiE7oblcQQa
    ZPkSSbu1w1Yi5lF2X/G7v2KNwFiGSbdbUDoBcleFyacI3HPcCleJ/7jaPbTB2r3G
    zkxMpU3bCuphznT4tWR5B2M11n494jghDKVmZhlq5KoZlRGDrBcLQbED+CH+FbGe
    EpD3XhU9NjSkpBodUbz9pKaiMpzW8jKMSxz1qOhbGcXnNYtNenrvDyfdxs9Gtggv
    khoSbnt5JJS8ffGliLWA2HoEY/YZxMN2B2KQwrDV9IPrxDiTOyk6N3pBqbGQJLlJ
    FQIDAQAB
    -----END PUBLIC KEY-----
    ''')

class HandlerPayOppo(BaseHandler):
    def post(self):
        cv.log("Got a oppo payment request...", True)
        reqResponse = ""
        try:
            notifyId = self.get_argument("notifyId")
            partnerOrder = self.get_argument("partnerOrder")
            productName = self.get_argument("productName")
            productDesc = self.get_argument("productDesc")
            price = self.get_argument("price")
            count = self.get_argument("count")
            attach = self.get_argument("attach")
            sign = self.get_argument("sign")
        except:
            reqResponse = "result=FAIL&resultMsg=Parameter error"
            self.write(reqResponse)
            self.flush()
            self.finish()

        nativeStr = "notifyId=%s&partnerOrder=%s&productName=%s&productDesc=%s&price=%s&count=%s&attach=%s" %(
            notifyId,
            partnerOrder,
            productName,
            productDesc,
            price,
            count,
            attach
            )
        cv.log("Native string:%s" % nativeStr, True)
        cv.log("Sign:%s" % sign, True)
        signNative = base64.decodestring(sign)
        cv.log("Sign native:%s" % signNative, True)
        try:
            isOk = rsa.verify(nativeStr, signNative, pubkey)
        except:
            isOk = False
        cv.log("result:%s" % isOk, True)
        url = "http://127.0.0.1:8080/oppo?price=%s&notifyId=%s&productName=%s&partnerOrder=%s&status=%s" %(price, notifyId, productName, partnerOrder, isOk)
        request = urllib2.Request(url)
        result = urllib2.urlopen(request).read()
        if True: # mySign == sign:
            reqResponse = "result=OK&resultMsg=OK"
        else:
            reqResponse = "result=FAIL&resultMsg=Sign error"
        self.write(reqResponse)
        self.flush()
        self.finish()
        