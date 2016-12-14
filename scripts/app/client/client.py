#coding:utf-8
import json
import hashlib
import random
import time
from app.basehandler import BaseHandler
from app.private import ranks

class Handler_CL_CheckPermission(BaseHandler):
    def get(self):
        
        gameInfo = self.application.mCfgInfo.mGameInfo
        r        = self.application.mCfgInfo.mRedisDB
        notice = r.hget("loginboard","content")
        maxPlayers = gameInfo["MaxPlayers"]
        version = gameInfo["Version"]
        version_ts = gameInfo["Version_TS"]
        ad = bool(gameInfo["AD"])
        canLogin = True
        self.write(json.dumps({"CanLogin": canLogin, "Version": version, "Version_TS": version_ts, "Notice": notice, "AD": ad}))
        self.flush()
        self.finish()

class Handler_CL_Ranks(BaseHandler):
    def get(self):
        serverID = self.get_argument("svrid")
        rankType = self.get_argument("t")
        rankKey = self.get_argument("k")
        r = self.application.mCfgInfo.mRedisDB
        result = ranks.GetAllRanks(r, serverID, rankType, rankKey)
        self.write(json.dumps(result))
        self.flush()
        self.finish()

class Handler_CL_ServerLists(BaseHandler):
    def get(self):
        serverlist = self.application.mCfgInfo.mServerList
        self.write(json.dumps(serverlist))
        self.flush()
        self.finish()

class Handler_CL_Login(BaseHandler):
    def get(self):
        r = self.application.mCfgInfo.mRedisDB
        username = self.get_argument("username")
        password = self.get_argument("password")
        identifyCode = ""
        hashedPassword = r.hget("account:%s" % (username.lower()), "password")
        if hashedPassword == hashlib.md5(password).hexdigest():
            identifyCode = hashlib.md5(username.lower() + str(random.randint(0, 100000)) + str(time.time())).hexdigest();
            if r.set(identifyCode, username.lower()):
                r.expire(identifyCode, 3600)
        self.write(identifyCode)
        self.flush()
        self.finish()

class Handler_CL_RegisterID(BaseHandler):
    def post(self):
        r = self.application.mCfgInfo.mRedisDB
        params = self.request.body.split('&')
        for valueStr in params:
            pair = valueStr.split('=')
            if pair[0] == 'token':
                r.sadd("Client_RegisterID", pair[1])
        self.write("Ok")
        self.flush()
        self.finish()