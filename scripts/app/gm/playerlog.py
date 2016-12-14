#coding:utf-8
import time
import json
import datetime
from app.basehandler import BaseHandler
from app.utils.zlhttpclient import zlHttpClient
from tornado.web import authenticated  

class Handler_PlayerLog(BaseHandler):
    @authenticated
    def get(self):
        svrNameById = self.application.mCfgInfo.mServerNameByID
        user = self.get_current_user()  
        self.render("%s/sm_playerlog.html"%(user["op"]), types=QRP.initOperations(), servers=svrNameById)

    def post(self):
        action = int(self.get_body_argument('action'))
        svrid = int(self.get_body_argument('svrid'))
        name = self.get_body_argument('plyname')
        #account = self.get_body_argument('account')
        account = ""
        beginstr = self.get_body_argument('bgntime')
        endstr = self.get_body_argument('endtime')
        try:
            startTime = time.mktime(time.strptime(beginstr, "%Y-%m-%d %H:%M"))
            endTime = time.mktime(time.strptime(endstr, "%Y-%m-%d %H:%M"))
            sendData = {"Action":action, "ServerID":svrid, "Name":name, "Account":account, "StartTime":startTime, "StopTime":endTime}
            httpClient = zlHttpClient()
            resultData = httpClient.sendToGM(sendData)
            jdata = json.loads(resultData)
            detail = json.loads(jdata["data"])
            msg = QRP.process(action, detail)
        except:
            msg = "Time format error！"
        self.write(json.dumps({"result":msg}))
        self.flush()
        self.finish()

from app.conf import * 

class QueryResultProcessor():
    def __init__(self):
        self.mQueryType = {
        }
        self.mCallBack = {
        }
        self.mHasInit = False
        # self.initOperations()

    def initOperations(self):
        if not self.mHasInit:
            self.mQueryType = {
            52:conf.Instance.scOperation(52),
            53:conf.Instance.scOperation(53),
            54:conf.Instance.scOperation(54),
            55:conf.Instance.scOperation(55),
            56:conf.Instance.scOperation(56),
            57:conf.Instance.scOperation(57),
            58:conf.Instance.scOperation(58),
            59:conf.Instance.scOperation(59),
            60:conf.Instance.scOperation(60),
            61:conf.Instance.scOperation(61),
            62:conf.Instance.scOperation(62),
            63:conf.Instance.scOperation(63),
            #64:"筋脉升级",
            65:conf.Instance.scOperation(65),
            #66:宝石合成,
            67:conf.Instance.scOperation(67),
            68:conf.Instance.scOperation(68),
            69:conf.Instance.scOperation(69),
            #100:"野外BOSS",
            #101:"野外击杀",
            102:conf.Instance.scOperation(102),
            #103:"交易跟踪",
            }
            self.mCallBack = {
            52:self.rechargeRecord,
            53:self.itemEvent,
            54:self.rewardsFromActivity,
            55:self.mailRecieve,
            56:self.buyFromMall,
            57:self.moneyChange,
            58:self.goldMoneyChange,
            59:self.sparChange,
            60:self.skillUpgrade,
            61:self.skillAdvance,
            62:self.talentUnlock,
            63:self.talentUpgrade,
            64:self.roleStrengthen,
            65:self.stoneEquip,
            66:self.stoneCombine,
            67:self.arenaRecord,
            68:self.equipUpgrade,
            69:self.equipAdvance,
            100:self.wildBoss,
            101:self.wildKill,
            102:self.tradeOperation,
            103:self.tradeTrace,
            }
            self.mHasInit = True
        return self.mQueryType

    def process(self, action, detail):
        if action in self.mCallBack:
            return self.mCallBack[action](detail)
        else:
            print "[ERROR]Can not find query result process handler! Action type:%s" %(action)
            return []

    def rechargeRecord(self, detail): # 52
        result = []
        for row in detail:
            sec = {}
            sec["Time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(row["RechargeTime"])))
            sec["Content"] = "[%s:%s]->[%s:%s]" %(conf.Instance.scSysString(0), row["RechargeAmount"], conf.Instance.scSysString(1), row["OrderSerial"])
            result.append(sec)
        return result

    def itemEvent(self, detail): # 53
        result = []
        for row in detail:
            sec = {}
            sec["Time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(row["LogTime"])))
            logType = row["EventType"]
            logName = conf.Instance.scLogtype(logType)
            if logType == 14:
                wayName = conf.Instance.scGetway(row["Way"])
            elif logType == 19:
                wayName = conf.Instance.scUseway(row["Way"])
            else:
                wayName = row["Way"]
            itemName = conf.Instance.getItemNameByID(row["ItemId"])
            count = row["ItemNumber"]
            try:
                desc = conf.Instance.scActivity(int(row["Description"]))
            except:
                desc = row["Description"]
            
            sec["Content"] = "[%s]->[%s]->[%s] %s x%d" %(logName, wayName, desc, itemName, count)
            result.append(sec)
        return result

    def rewardsFromActivity(self, detail): # 54
        result = []
        for row in detail:
            sec = {}
            sec["Time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(row["RewardTime"])))
            logtype = row["RewardType"]
            logName = conf.Instance.scLogtype(logtype)
            actName = conf.Instance.scActivity(int(row["ActivityId"]))
            resType = [11,12,13,15,16,30,31,54]
            if logtype in resType:
                count = row["Number"]
                info = "[%s]->[%s] x%d" %(logName, actName, count)
            elif logtype == 14:
                itemName = conf.Instance.getItemNameByID(row["ItemId"])
                count = row["ItemNumber"]
                info = "[%s]->[%s] %s x%d" %(logName, actName, itemName, count)
            else:
                info = "Invalid"
            sec["Content"] = info
            result.append(sec)
        return result

    def mailRecieve(self, detail): # 55
        result = []
        for row in detail:
            sec = {}
            
            ress = row["Res"].split(";")
            resInfo = ""
            for resstr in ress:
                resarr = resstr.split(",")
                if len(resarr) == 2:
                    resName = conf.Instance.scRestype(int(resarr[0]))
                    resCount = resarr[1]
                    resInfo += " ⊙ " + resName + " x " + resCount
            items = row["Items"].split(";")
            itemInfo = ""
            for itemstr in items:
                itemarr = itemstr.split(",")
                if len(itemarr) == 3:
                    itemName = conf.Instance.getItemNameByID(int(itemarr[1]))
                    itemCount = itemarr[2]
                    itemInfo += " ⊙ " + itemName + " x " + itemCount
            sec["Time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(row["SendTime"])))
            msg = "[%s:%s]</br>[%s:%s]</br>[%s:%s]</br>[%s:%s]" %(
                conf.Instance.scSysString(2),
                row["MailHead"],
                conf.Instance.scSysString(3),
                row["MailBody"], 
                conf.Instance.scSysString(4),
                resInfo, 
                conf.Instance.scSysString(5),
                itemInfo)
            sec["Content"] = msg
            result.append(sec)
        return result

    def buyFromMall(self, detail): # 56
        result = []
        for row in detail:
            sec = {}
            sec["Content"] = "[%s] %s x %s" %(conf.Instance.scSysString(6), conf.Instance.getItemNameByID(row["ItemId"]), row["ItemNumber"])
            sec["Time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(row["RewardTime"])))
            result.append(sec)
        return result

    def moneyChange(self, detail): # 57
        result = []
        for row in detail:
            sec = {}
            sec["Time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(row["LogTime"])))
            logtype = row["LogType"]
            logName = conf.Instance.scLogtype(logtype)
            if logtype == 11:
                wayName = conf.Instance.scGetway(row["Param0"])
            elif logtype == 17:
                wayName = conf.Instance.scUseway(row["Param0"])
            else:
                wayName = row["Param0"]
            try:
                desc = conf.Instance.scActivity(int(row["Desc"]))
            except:
                desc = row["Desc"]
            sec["Content"] = "[%s]->[%s]->[%s] %s:%s %s:%s" %(logName, wayName, desc, conf.Instance.scSysString(7), row["Param1"], conf.Instance.scSysString(8), row["Param3"])
            result.append(sec)
        return result

    def goldMoneyChange(self, detail): # 58
        result = []
        for row in detail:
            sec = {}
            sec["Time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(row["LogTime"])))
            logtype = row["LogType"]
            logName = conf.Instance.scLogtype(logtype)
            if logtype == 12 or logtype == 13:
                wayName = conf.Instance.scGetway(row["Param0"])
            elif logtype == 18:
                wayName = conf.Instance.scUseway(row["Param0"])
            else:
                wayName = row["Param0"]
            try:
                desc = conf.Instance.scActivity(int(row["Desc"]))
            except:
                desc = row["Desc"]
            sec["Content"] = "[%s]->[%s]->[%s] %s:%s %s:%s" %(logName, wayName, desc, conf.Instance.scSysString(7), row["Param1"], conf.Instance.scSysString(8), row["Param3"])
            result.append(sec)
        return result

    def sparChange(self, detail): # 59
        result = []
        for row in detail:
            sec = {}
            sec["Time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(row["LogTime"])))
            logtype = row["LogType"]
            logName = conf.Instance.scLogtype(logtype)
            if logtype == 31:
                wayName = conf.Instance.scGetway(row["Param0"])
            elif logtype == 32:
                wayName = conf.Instance.scUseway(row["Param0"])
            else:
                wayName = row["Param0"]
            try:
                desc = conf.Instance.scActivity(int(row["Desc"]))
            except:
                desc = row["Desc"]
            sec["Content"] = "[%s]->[%s]->[%s] %s:%s %s:%s" %(logName, wayName, desc, conf.Instance.scSysString(7), row["Param1"], conf.Instance.scSysString(8), row["Param3"])
            result.append(sec)
        return result

    def skillUpgrade(self, detail): # 60
        result = []
        for row in detail:
            sec = {}
            sec["Time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(row["LogTime"])))
            sec["Content"] = "[%s:%s]->[%s:%s] %s:%s" %(conf.Instance.scLogtype(34), conf.Instance.mSkillInfo[int(row["Param0"])], conf.Instance.scSysString(9), row["Param1"], conf.Instance.scSysString(10), row["Param2"])
            result.append(sec)
        return result

    def skillAdvance(self, detail): # 61
        result = []
        for row in detail:
            sec = {}
            sec["Time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(row["LogTime"])))
            sec["Content"] = "[%s:%s]->[%s:%s]" %(conf.Instance.scLogtype(35), conf.Instance.mSkillInfo[int(row["Param0"])], conf.Instance.scSysString(9), row["Param1"])
            result.append(sec)
        return result

    def talentUnlock(self, detail): # 62
        result = []
        for row in detail:
            sec = {}
            sec["Time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(row["LogTime"])))
            sec["Content"] = "[%s:%s(%s)]" %(conf.Instance.scLogtype(36), row["Param0"], conf.Instance.mTalentUnlock[int(row["Param0"])])
            result.append(sec)
        return result

    def talentUpgrade(self, detail): # 63
        result = []
        for row in detail:
            sec = {}
            sec["Time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(row["LogTime"])))
            sec["Content"] = "[%s:%s(%s)->%s(%s)]" %(conf.Instance.scLogtype(37), row["Param2"], conf.Instance.mTalentUpgrade[int(row["Param0"])], row["Param3"], conf.Instance.mTalentUpgrade[int(row["Param0"])])
            result.append(sec)
        return result

    def roleStrengthen(self, detail): # 64
        result = []
        for row in detail:
            sec = {}
            sec["Time"] = "2097-06-09 00:12:44" # time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(row["LogTime"])))
            sec["Content"] = "I will back!" # "[%s:%s->%s]" %(conf.Instance.scLogtype(37), row["Param2"], row["Param3"])
            result.append(sec)
        return result

    def stoneEquip(self, detail): # 65
        result = []
        for row in detail:
            sec = {}
            sec["Time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(row["LogTime"])))
            sec["Content"] = "[%s:%s]->[%s:%s]->[%s:%s]" %(
                conf.Instance.scLogtype(row["LogType"]), 
                conf.Instance.getItemNameByID(row["Param0"]), 
                conf.Instance.scSysString(11),
                conf.Instance.scEquippos(row["Param1"]), 
                conf.Instance.scSysString(12),
                row["Param2"])
            result.append(sec)
        return result

    def stoneCombine(self, detail): # 66
        result = []
        for row in detail:
            sec = {}
            sec["Time"] = "2097-06-09 00:12:44" # time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(row["LogTime"])))
            sec["Content"] = "I will back!" # "[%s:%s->%s]" %(conf.Instance.scLogtype(37), row["Param2"], row["Param3"])
            result.append(sec)
        return result

    def arenaRecord(self, detail): # 67
        result = []
        for row in detail:
            sec = {}
            sec["Time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(row["LogTime"])))
            sec["Content"] = "[%s][%s:%s]->[%s:%s]" %(
                conf.Instance.scLogtype(39), 
                conf.Instance.scSysString(13),
                row["Param0"], 
                conf.Instance.scSysString(14),
                row["Param3"])
            result.append(sec)
        return result

    def equipUpgrade(self, detail): # 68
        result = []
        for row in detail:
            sec = {}
            sec["Time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(row["LogTime"])))
            sec["Content"] = "[%s]->[%s]->[%s:%s]" %(
                conf.Instance.scLogtype(21), 
                conf.Instance.scEquippos(row["Param0"]), 
                conf.Instance.scSysString(15),
                row["Param1"])
            result.append(sec)
        return result

    def equipAdvance(self, detail): # 69
        result = []
        for row in detail:
            sec = {}
            sec["Time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(row["LogTime"])))
            sec["Content"] = "[%s]->[%s]->[%s:%s]" %(
                conf.Instance.scLogtype(22), 
                conf.Instance.scEquippos(row["Param0"]), 
                conf.Instance.scSysString(15),
                row["Param3"])
            result.append(sec)
        return result

    def wildBoss(self, detail): # 100
        result = []
        for row in detail:
            sec = {}
            sec["Time"] = "2097-06-09 00:12:44" # time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(row["LogTime"])))
            sec["Content"] = "I will back!" # "[%s:%s->%s]" %(conf.Instance.scLogtype(37), row["Param2"], row["Param3"])
            result.append(sec)
        return result

    def wildKill(self, detail): # 101
        result = []
        for row in detail:
            sec = {}
            sec["Time"] = "2097-06-09 00:12:44" # time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(row["LogTime"])))
            sec["Content"] = "I will back!" # "[%s:%s->%s]" %(conf.Instance.scLogtype(37), row["Param2"], row["Param3"])
            result.append(sec)
        return result

    def tradeOperation(self, detail): # 102
        result = []
        for row in detail:
            sec = {}
            sec["Time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(row["LogTime"])))
            sec["Content"] = "[%s]->[%s]->[%s]" %(conf.Instance.scTradeop(row["OpType"]), conf.Instance.getItemNameByID(row["ItemId"]), row["Detail"])
            result.append(sec)
        return result

    def tradeTrace(self, detail): # 103
        result = []
        for row in detail:
            sec = {}
            sec["Time"] = "2097-06-09 00:12:44" # time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(row["LogTime"])))
            sec["Content"] = "I will back!" # "[%s:%s->%s]" %(conf.Instance.scLogtype(37), row["Param2"], row["Param3"])
            result.append(sec)
        return result

QRP = QueryResultProcessor()
