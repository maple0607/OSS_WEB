#coding=utf8
import time
import os
import json
import base64
import traceback
import threading
from app.private import ranks, rankawardcfg
from app.utils.mailhelper import MailHelper
from app.basehandler import BaseHandler
from app.conf.stringtable import *

Award_Count = 10

class Handler_Ranks_Award(BaseHandler):
    def get(self):
        self.application.checkPermission(self)

        r = self.application.mCfgInfo.mRedisDB

        serverID = self.get_argument("svrid")
        print("Handler_Ranks_Award:" + serverID)

        rankKey = 123
        levelResult = ranks.GetAllRanks(r, serverID, 0, rankKey)
        bpResult = ranks.GetAllRanks(r, serverID, 2, rankKey)
        rankDatas = [levelResult, bpResult]

        self.write(json.dumps(rankDatas))
        self.flush()
        self.finish()

        if r.setnx("rank_award_done:%s" % (serverID), "1"):
            t = threading.Thread(target=self.GiveAward, args=(rankDatas,serverID))
            t.start()
        else:
            print("have award return : " + str(serverID))
            return

    def GiveAward(self, rankDatas, serverID):
        # 发奖励
        #rewards = [[5,55080001,100], [4,44330001,100], [2,2000]]
        mailH = MailHelper()
        # 等级排行
        title = "等级排名奖励"
        num = 0
        for rank in rankDatas[0]["ranks"]:
            print rank["n"]
            titleAndContent = "%s^%s" % (title, rankawardcfg.LevelRankRewards[num][1])
            rewards = rankawardcfg.LevelRankRewards[num][0]
            print(rewards)
            mailH.sendmail(serverID, rank["n"], titleAndContent, rewards)
            num += 1
            if num >= Award_Count:   # 只发前10
                break

        # 战力排行
        num = 0
        title = "战力排名奖励"
        for rank in rankDatas[1]["ranks"]:
            print rank["n"]
            titleAndContent = "%s^%s" % (title, rankawardcfg.PowerRankRewards[num][1])
            rewards = rankawardcfg.PowerRankRewards[num][0]
            mailH.sendmail(serverID, rank["n"], titleAndContent, rewards)
            num += 1
            if num >= Award_Count: # 只发前10
                break