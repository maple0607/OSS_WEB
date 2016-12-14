#coding:utf-8
import hmac
import hashlib
import urllib
import urllib2
import rsa
import time
import datetime
import base64
from app.basehandler import BaseHandler
from app.utils.zlhttpclient import zlHttpClient
from app.utils.views import *
import traceback
import hashlib
import json
import time
from M2Crypto import RSA,EVP,BIO
import base64

pubkey = '''-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDDowkl/ig8hjZ5FXblGPIZmYRR
6KyRWQg9adkgmKz4L4T38OksrxO/ehSb5Qp2qx1VijJ1Z0xX8SznM8/0kW+p/fg2
jW1W2CjjvcwSh4q0beBZZGF9UfgVHFHEEQFUFpa1cvH0+Qbd4IIsGBwiCM3aFNOr
mCRdnQVt4eZqV9jbPQIDAQAB
-----END PUBLIC KEY-----'''

pubkey_ios = '''-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDSY/auUx9Q/DiuPGB6/SoiCgqE
ES+BCr7KGWtFjDJJveg5XN3+SQ9lbceTOEK52GOd4nsnjFG06kaab6pb9qEO7krR
f6+rkcJ8CqznRaOdBEbQs8X9KDgyAYW+xfVAB7XbsTUWJgTk5iSmUZHGAQVJJu2x
HIxsCTUh7P+6RhkfsQIDAQAB
-----END PUBLIC KEY-----'''

class HandlerPay7659(BaseHandler):
    def post(self):
        cv.log("Got a 7659 payment request...", True)
        reqResponse = ""
        keyValues = {}
        try:
            keyValues["notify_data"] = self.get_argument("notify_data")
            keyValues["orderid"] = self.get_argument("orderid")
            keyValues["dealseq"] = self.get_argument("dealseq")
            keyValues["uid"] = self.get_argument("uid")
            keyValues["subject"] = self.get_argument("subject")
            keyValues["v"] = self.get_argument("v")
            sign = self.get_argument("sign")
        except:
            reqResponse = "failed"
            cv.log("Parameter parse error!", True)
            cv.flush()
            self.write(reqResponse)
            self.flush()
            self.finish()

        # step 1
        platform = "adr"
        isOk = self._gen_sign(keyValues, sign, pubkey)
        cv.log("Step 1 - check sign with adr_key finish, result:%s" % isOk, True)

        if not isOk:
            isOk = self._gen_sign(keyValues, sign, pubkey_ios)
            cv.log("Step 2 - check sign with ios_key finish, result:%s" % isOk, True)
            platform = "ios"

        if isOk:
            # step 2
            if platform == "adr":
                finalData = self.check_pay(keyValues, pubkey)
            else:
                finalData = self.check_pay(keyValues, pubkey_ios)
            if "fee" in finalData:
                url = "http://127.0.0.1:8080/7659?price=%s&orderId=%s&productName=%s&partnerOrder=%s&status=%s" %(finalData["fee"], finalData["orderid"], finalData["subject"], finalData["dealseq"], isOk)
                request = urllib2.Request(url)
                result = urllib2.urlopen(request).read()
                cv.log("Step 2 request sending", True)
            else:
                cv.log("Step 2 check failed", True)
            reqResponse = "success"
        else:
            reqResponse = "failed"
        cv.flush()
        self.write(reqResponse)
        self.flush()
        self.finish()

    def urlDecode(self, string):
        return urllib.unquote_plus(string)

    def _gen_sign(self, params, sign, pub_key):
        data = [(k, v,) for k, v in params.iteritems()]
        sorted_data = sorted(data, key=lambda x : x[0], reverse=False)
        list_data = ['%s=%s' % (str(k.encode("utf-8")),str(v.encode("utf-8"))) for k, v in sorted_data]
        sgtr = '&'.join(list_data)
        cv.log(sgtr, True)
        try:
            key = RSA.load_pub_key_bio(BIO.MemoryBuffer(pub_key))
            m = EVP.MessageDigest('sha1')
            m.update(sgtr)
            digest = m.final()
            signature = False
            signature = key.verify(digest, base64.decodestring(sign), "sha1")
            return signature
        except Exception, e:
            traceback.print_exc()
        
        return False

    def check_pay(self, data, pub_key):
        try:
            if "notify_data" in data:
                notify_data = data.get('notify_data')
                grsa = RSA.load_pub_key_bio(BIO.MemoryBuffer(pub_key))
                ctxt = grsa.public_decrypt(base64.b64decode(notify_data), RSA.pkcs1_padding)
                obj = dict((l.split('=') for l in ctxt.split('&')))
                if int(obj.get('payresult')) == 0 and obj.get('dealseq') == data.get("dealseq"):
                    data['payresult'] = obj.get('payresult')
                    data['fee'] = obj.get("fee")
                    return data
        except Exception, e:
            traceback.print_exc()
        return data

   

    