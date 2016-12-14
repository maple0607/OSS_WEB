#coding:utf-8
import urllib
import urllib2
import json
import os
import base64
import hashlib
import time
from app.conf.conf import Instance
class zlHttpClient:
    def __init__(self):
        pass
    def sendToGM(self, jData):
        jData["OperatorID"] = 1

        encodedData = base64.b64encode(json.dumps(jData))
        sign = hashlib.sha1(encodedData + Instance.mGmServerKey).hexdigest()
        responseData = json.dumps({"data":json.dumps(jData),"sign":sign}, sort_keys=True)
        request = urllib2.Request("%s?sign=%s" %(Instance.mGmServerUrl, sign))
        request.add_data(responseData)
        response = urllib2.urlopen(request)
        resultData = response.read()
        return resultData