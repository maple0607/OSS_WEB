#coding=utf8

from tornado.gen import coroutine, Return
from app.basehandler import BaseHandler
import hashlib
import urllib
import time
import random
class Handler_Check_Authorize(BaseHandler):
    @coroutine
    def get(self):
        deviceId = self.get_argument("identifier")
        fbAccount = self.get_argument("fbaccount")
        if int(self.application.mPort) == 8280:
            account = yield VAM.getAccount(deviceId, fbAccount)
            identifyCode = hashlib.md5(str(account).lower() + str(random.randint(0, 100000)) + str(time.time())).hexdigest()
            resultStr = "%s:%s" %(account, identifyCode)
        else:
            ipStr = "127.0.0.1:8280"
            paramDict = {}
            paramDict["identifier"] = deviceId
            paramDict["fbaccount"]  = fbAccount
            params=urllib.urlencode(paramDict)
            f = urllib.urlopen("http://%s/vertifyaccount?%s" % (ipStr, params))
            resultStr = f.read()
        self.write(resultStr)
        self.flush()
        self.finish()

from app.conf import *
#import fcntl
import os

FOLDER = "data"
FILE = "AccCount.txt"

class VisitorAccountMgr():
    def __init__(self):
        self.mAccDB = None
        self.init()
        
    def init(self):
        if not os.path.isdir(FOLDER):
            os.mkdir(FOLDER)
        if not os.path.exists(FOLDER + '/' + FILE):
            f_hdr = open(FOLDER + '/' + FILE, "w")
            f_hdr.write("7654321")
            f_hdr.close()

    @coroutine
    def getAccount(self, deviceId, fbAccount):
        self.mAccDB = conf.Instance.mAccDB
        AccCount = 0
        #f_hdr = open(FOLDER + '/' + FILE, "r+")
        #fcntl.flock(f_hdr.fileno(), fcntl.LOCK_EX)
        #data = f_hdr.read()
        '''try:
            AccCount = int(data)
        except:
            f_hdr.close()
            raise Return(AccCount)'''
        if fbAccount == "":
            querySQL = "select * from Accounts where DeviceID = '%s' and FBAccount = ''" %(deviceId)
            hdr = yield self.mAccDB.execute(querySQL)
            result = hdr.fetchone()
            if result != None and len(result) == 3 and result[2] != None:
                account  = result[2]
            else:
                f_hdr = open(FOLDER + '/' + FILE, "r+")
                data = f_hdr.read()
                try:
                    AccCount = int(data)
                except:
                    f_hdr.close()
                    raise Return(AccCount)
                account = AccCount
                AccCount += 1
                f_hdr.seek(0)
                f_hdr.write(str(AccCount))
                f_hdr.close()
                querySQL = "insert into Accounts values('%s', '', '%s')" %(deviceId, account)
                yield self.mAccDB.execute(querySQL)
        else:
            querySQL = "select * from Accounts where FBAccount = '%s'" %(fbAccount)
            hdr = yield self.mAccDB.execute(querySQL)
            result = hdr.fetchone()
            if result != None and len(result) == 3 and result[2] != None:
                account  = result[2]
            else:
                querySQL = "select * from Accounts where DeviceID = '%s' and FBAccount = ''" %(deviceId)
                hdr = yield self.mAccDB.execute(querySQL)
                result = hdr.fetchone()
                if result != None and len(result) == 3 and result[2] != None:
                    querySQL = "update Accounts set FBAccount = '%s' where DeviceID = '%s' and FBAccount = ''" %(fbAccount, deviceId)
                    yield self.mAccDB.execute(querySQL)
                    account  = result[2]
                else:
                    f_hdr = open(FOLDER + '/' + FILE, "r+")
                    data = f_hdr.read()
                    try:
                        AccCount = int(data)
                    except:
                        f_hdr.close()
                        raise Return(AccCount)
                    account = AccCount
                    AccCount += 1
                    f_hdr.seek(0)
                    f_hdr.write(str(AccCount))
                    f_hdr.close()
                    querySQL = "insert into Accounts values('%s', '%s', '%s')" %(deviceId, fbAccount, account)
                    yield self.mAccDB.execute(querySQL)
        raise Return(account)

    @coroutine
    def getAccountEx(self, deviceId, fbAccount):
        account = ""
        if fbAccount == "":
            querySQL = "select * from Accounts where DeviceID = '%s' and FBAccount = ''" %(deviceId)
            hdr = yield self.mAccDB.execute(querySQL)
            result = hdr.fetchone()
            if result != None and len(result) == 3 and result[2] != None:
                account  = result[2]
            else:
                account = self.mNextAccount
                self.mNextAccount += 1
                querySQL = "update AccCount set Count = %s where Count = %s" %(self.mNextAccount, account)
                yield self.mAccDB.execute(querySQL)
                querySQL = "insert into Accounts values('%s', '%s', '%s')" %(deviceId, "", account)
                yield self.mAccDB.execute(querySQL)
        else:
            querySQL = "select * from Accounts where FBAccount = '%s'" %(fbAccount)
            hdr = yield self.mAccDB.execute(querySQL)
            result = hdr.fetchone()
            if result != None and len(result) == 3 and result[2] != None:
                account  = result[2]
            else:
                querySQL = "select * from Accounts where DeviceID = '%s' and FBAccount = ''" %(deviceId)
                hdr = yield self.mAccDB.execute(querySQL)
                result = hdr.fetchone()
                if result != None and len(result) == 3 and result[2] != None:
                    querySQL = "update Accounts set FBAccount = '%s' where DeviceID = '%s' and FBAccount = ''" %(fbAccount, deviceId)
                    yield self.mAccDB.execute(querySQL)
                    account  = result[2]
                else:
                    account = self.mNextAccount
                    self.mNextAccount += 1
                    querySQL = "update AccCount set Count = %s where Count = %s" %(self.mNextAccount, account)
                    yield self.mAccDB.execute(querySQL)
                    querySQL = "insert into Accounts values('%s', '%s', '%s')" %(deviceId, fbAccount, account)
                    yield self.mAccDB.execute(querySQL)
        raise Return(account)

VAM = VisitorAccountMgr()