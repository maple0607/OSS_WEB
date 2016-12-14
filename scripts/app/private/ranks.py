#coding=utf8

import tornadoredis
import tornado.web
import tornado.gen
import tornado.httpserver
import tornado.web
import tornado.ioloop
import tornado.options
import time
import os
import json
import base64
import traceback
from app.basehandler import BaseHandler
dataFolder = "data/ranks/"
rankReverse = {
    "0":True,   # Level
    "1":True,   # VipLevel
    "2":True,   # BattlePoint
    "3":False,  # Endless
}

class Handler_Update_Ranks(BaseHandler):
    def get(self):
        self.application.checkPermission(self)

        r = self.application.mCfgInfo.mRedisDB

        serverID = self.get_argument("svrid")
        rankType = self.get_argument("t")
        rankKey = self.get_argument("k")
        rankScore = self.get_argument("v")
        rankData = self.get_argument("d")

        maxRanks = 50
        isReverse = True
        if rankType in rankReverse:
            isReverse = rankReverse[rankType]

        keyName = "ranks:%s:%s" % (serverID, rankType)
        singleKeyName = "ranks:%s:%s:%s" % (serverID, rankType, rankKey)
        p = r.pipeline()
        p.zadd(keyName, rankKey, rankScore)
        p.set(singleKeyName, rankData)
        p.expire(singleKeyName, 30)
        p.zcard(keyName)
        ret = p.execute()

        if ret[3] != None:
            if ret[3] > maxRanks:
                if isReverse:
                    r.zremrangebyrank(keyName, 0, -(maxRanks + 1))
                else:
                    r.zremrangebyrank(keyName, maxRanks, -1)
        

        if not os.path.exists(dataFolder):
            os.makedirs(dataFolder)

        filename = dataFolder + base64.b64encode(singleKeyName)
        dataFile = open(filename, "wb")
        dataFile.write(rankData)
        dataFile.close()

        self.write(str(ret))
        self.flush()
        self.finish()

def GetAllRanks(r, serverID, rankType, rankKey):
        keyName = "ranks:%s:%s" % (serverID, rankType)
        cacheKeyName = "ranks:%s:%s:cache" % (serverID, rankType)

        isReverse = True
        if rankType in rankReverse:
            isReverse = rankReverse[rankType]

        cacheData = r.get(cacheKeyName)
        if cacheData == None:
            needRefreshData = {}

            ranksData = []
            ranks = r.zrange(keyName, 0, -1)

            if len(ranks) > 0:
                rankKeys = ["ranks:%s:%s:%s" % (serverID, rankType, _key) for _key in ranks]
                _ranksData = r.mget(ranks)

                for i in xrange(len(_ranksData)):
                    data = _ranksData[i]
                    if data == None:
                        singleKeyName = rankKeys[i]
                        filename = dataFolder + base64.b64encode(singleKeyName)
                        if os.path.exists(filename):
                            dataFile = open(filename, "rb")
                            data = dataFile.read()
                            dataFile.close()
                            needRefreshData[singleKeyName] = data

                    if data == None:
                        ranksData.append({})
                    else:
                        ranksData.append(json.loads(data))

                if len(needRefreshData) > 0:
                    p = r.pipeline()
                    for k in needRefreshData:
                        data = needRefreshData[k]
                        p.set(k, data)
                        p.expire(k, 3)
                    p.execute()

                if isReverse:
                    ranksData.reverse()

            result = {
                "type": rankType,
                "ranks": ranksData,
            }

            cacheData = json.dumps(result)
            p = r.pipeline()
            p.set(cacheKeyName, cacheData)
            p.expire(cacheKeyName, 30)
            p.execute()

        result = json.loads(cacheData)

        selfKeyName = "ranks:%s:%s:%s" % (serverID, rankType, rankKey)
        selfRankData = r.get(selfKeyName)
        if selfRankData == None:
            filename = dataFolder + base64.b64encode(selfKeyName)
            if os.path.exists(filename):
                dataFile = open(filename, "rb")
                selfRankData = dataFile.read()
                dataFile.close()

        if selfRankData == None:
            result["selfRank"] = {}
        else:
            result["selfRank"] = json.loads(selfRankData)

        if isReverse:
            selfRank = r.zrevrank(keyName, rankKey)
        else:
            selfRank = r.zrank(keyName, rankKey)

        if selfRank == None:
            result["selfRank"]["rank"] = -1
        else:
            result["selfRank"]["rank"] = selfRank + 1

        return result
