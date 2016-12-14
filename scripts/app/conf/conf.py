#coding:utf-8
import json
import copy
import redis
import sys
import os
from tornado_mysql import pools
from app.utils.tabfile import TabFile
from app.utils.views import *
from app.analysis.analysismanager import *
from app.conf.stringtable import *

CONFIG_PATH = "configs/"
SL_BACKUP = "serverlist_backup/"

#string category id
SC_BACKUP   = 0 # 备用
SC_LOGTYPE  = 1
SC_USEWAY   = 2
SC_GETWAY   = 3
SC_ACTIVITY = 4
SC_EQUIPPOS = 5
SC_TRADEOP  = 6
SC_RESTYPE  = 7
SC_OPERATION = 10
SC_SYSSTRING = 11
SC_SUBSISTENCE = 12
SC_BORDER = 1000

# serverlist policy
SP_MANUAL   = -1 # 手动（手动调整状态）
SP_CURRENCY = 0  # 实时动态（自动切换状态）
SP_ROLLING  = 1  # 滚服（均衡导入，自动切换状态/顺序）
SP_POPULARITY = 2 # 人气策略（置顶服为新服，其余为火爆）
POLICIES = {
    SP_MANUAL     : ST("手动策略"),
    SP_CURRENCY   : ST("实时策略"),
    SP_ROLLING    : ST("滚服策略"),
    SP_POPULARITY : ST("人气策略")
}

SIMPLE_POLICIES = {
    SP_MANUAL : ST("状态手动"),
    SP_CURRENCY : ST("状态自动")
}

# serverlist status

SS_GOOD      = 1 # 良好
SS_FULL      = 2 # 爆满
SS_HOT       = 3 # 火爆
SS_NEW       = 4 # 新增
SS_RECOMMEND = 5 # 推荐

STATUS = {
SS_GOOD      : ST("良好"),
SS_FULL      : ST("爆满"),
SS_HOT       : ST("火爆"),
SS_NEW       : ST("新增"),
SS_RECOMMEND : ST("推荐")
}

STATUS_LEVEL = [
    [800, SS_FULL],
    [600, SS_HOT],
    [400, SS_GOOD],
    [0  , SS_RECOMMEND],
]

QUALITIES = {
    0  : ST("绿色"),
    1  : ST("绿色"),
    2  : ST("绿色"),
    3  : ST("蓝色"),
    4  : ST("蓝色"),
    5  : ST("蓝色"),
    6  : ST("紫色"),
    7  : ST("紫色"),
    8  : ST("紫色"),
    9  : ST("橙色"),
    10 : ST("橙色"),
    11 : ST("橙色"),
    12 : ST("红色"),
    13 : ST("红色"),
    14 : ST("红色"),
}

GMPORT = 8888

class ServerConfig:
    def __init__(self):
        self.mServicePort = 80
        self.mAppPort = 0
        self.mIsDebug = True
        self.mPermissionIP = []
        self.mRedisDB = {}
        self.mWebDB = {}
        self.mGMDB = {}
        self.mAccDB = {}
        self.mAnaDB = {}
        self.mPayDB = {}
        self.mServerList = []
        self.mGmServerUrl = ""
        self.mPayServerAddr = ""
        self.mLoginBoard = ""
        self.mGameInfo = {}
        self.mServerNameByID = {}
        self.mBackupFiles = {}
        self.mSortBackup = []
        self.mServerListFIle = ""
        self.mCurView = ""
        self.mRevertCache = [None, None]
        self.mServerListPolicy = SP_MANUAL
        #道具
        self.mItemsByName = {}
        self.mItemsById = {}
        self.mItemQualityById = {}
        self.mPetInfo = {}
        self.mPetType = {}
        self.mPetTalent = {}
        self.mSkillInfo = {}
        self.mTalentUpgrade = {}
        self.mTalentUnlock = {}
        self.mGuildLevel = {}
        #字串表
        self.mStringTable = {}
        self.mLanguage = 0

    def startup(self, cfgfile = "configs/main.json", port = 0):
        self.mAppPort = int(port)
        cfgHandler = open(cfgfile)
        cfgdata = cfgHandler.read()
        cfgHandler.close()
        jsonData = json.loads(cfgdata)
        self.mServicePort = int(jsonData["ServicePort"])
        self.mIsDebug = bool(jsonData["Debug"])
        self.mPermissionIP = copy.deepcopy(jsonData["PermissionIP"])
        self.mGmServerUrl = jsonData["GMServerUrl"]
        self.mGmServerKey = jsonData["GMServerKey"]
        self.mPayServerAddr = jsonData["PayServerAddr"]
        self.mGameInfo = jsonData["Game"]

        cv.log("Connecting to redis ...", True)
        try:
            self.mRedisDB = redis.Redis(
                jsonData["Redis"]["Hostname"],
                int(jsonData["Redis"]["Hostport"]),
                int(jsonData["Redis"]["Database"]),
                jsonData["Redis"]["Password"]
                )
        except:
            self.mRedisDB = redis.Redis(
                jsonData["Redis"]["Hostname"],
                int(jsonData["Redis"]["Hostport"]),
                int(jsonData["Redis"]["Database"])
                )
        cv.log("Connecting to redis OK.", True)

        cv.log("Connecting to WebDB ...", True)
        self.mWebDB = pools.Pool(
            dict(
               host=jsonData["WebCenter"]["Hostname"], 
               port=jsonData["WebCenter"]["Hostport"], 
               user=jsonData["WebCenter"]["Username"], 
               passwd=jsonData["WebCenter"]["Password"], 
               db=jsonData["WebCenter"]["Database"],
               charset="utf8"),
           max_idle_connections=jsonData["WebCenter"]["Connections"],
           max_recycle_sec=3
            )
        cv.log("Connecting to WebDB OK.", True)

        cv.log("Connecting to GMDB ...", True)
        self.mGMDB = pools.Pool(
            dict(
               host=jsonData["GmDb"]["Hostname"], 
               port=jsonData["GmDb"]["Hostport"], 
               user=jsonData["GmDb"]["Username"], 
               passwd=jsonData["GmDb"]["Password"], 
               db=jsonData["GmDb"]["Database"],
               charset="utf8"),
           max_idle_connections=jsonData["GmDb"]["Connections"],
           max_recycle_sec=3
            )
        cv.log("Connecting to GMDB OK.", True)

        cv.log("Connecting to AccDB ...", True)
        self.mAccDB = pools.Pool(
            dict(
                host=jsonData["AccDB"]["Hostname"], 
                port=jsonData["AccDB"]["Hostport"], 
                user=jsonData["AccDB"]["Username"], 
                passwd=jsonData["AccDB"]["Password"], 
                db=jsonData["AccDB"]["Database"],
                charset="utf8"
                ),
            max_idle_connections=jsonData["AccDB"]["Connections"],
            max_recycle_sec=3
            )
        cv.log("Connecting to AccDB OK.", True)

        cv.log("Connecting to AccDB ...", True)
        self.mPayDB = pools.Pool(
            dict(
                host=jsonData["PayDB"]["Hostname"],
                port=jsonData["PayDB"]["Hostport"],
                user=jsonData["PayDB"]["Username"],
                passwd=jsonData["PayDB"]["Password"],
                db=jsonData["PayDB"]["Database"],
                charset="utf8"
                ),
            max_idle_connections=jsonData["PayDB"]["Connections"],
            max_recycle_sec=3
            )
        cv.log("Connecting to PayDB OK.", True)

        cv.log("Connecting to AnaDB ...", True)
        AnaMgr.startup("Analysis", -1, "result", 
            jsonData["AnaDB"]["Username"],
            jsonData["AnaDB"]["Password"],
            jsonData["AnaDB"]["Hostname"],
            jsonData["AnaDB"]["Hostport"],
            jsonData["AnaDB"]["Database"])
        cv.log("Connecting to AnaDB OK.", True)

        cv.log("Loading ServerList ...", True)
        self.mServerListFIle = jsonData["ServerList"][0]
        if not self.loadServerList(jsonData["ServerList"]):
            sys.exit(-1)
        cv.log("Loading ServerList OK.", True)
        cv.log("Loading ItemData ...", True)
        self.loadItems(jsonData["ItemsDir"])
        cv.log("Loading ItemData OK.", True)
        self.loadGuildLevel()
        self.loadStringTable()
        return self

    def isGMClient(self):
        return self.mAppPort == GMPORT

    def loadGuildLevel(self, fn = "configs/guildlevel.txt"):
        try:
            cv.log("Loading guild level ...", True)
            tb = TabFile()
            if tb.load(fn):
                for i in xrange(tb.mRowNum):
                    level     = tb.get(i, 0, 0, True)
                    exp       = tb.get(i, 1, 0, True)
                    membermax = tb.get(i, 2, 0, True)
                    self.mGuildLevel[level] = [exp, membermax]
            cv.log("Loading guild level OK.", True)
        except:
            cv.err("Loading guild level failed!", True)

    def loadStringTable(self, fn = "configs/stringtable/id.txt"):
        try:
            cv.log("Loading string table ...", True)
            tb = TabFile()
            if tb.load(fn):
                for i in xrange(tb.mRowNum):
                    stringID = tb.get(i, 0, 0, True)
                    lans = []
                    for j in xrange(1, tb.mColNum):
                        lans.append(tb.get(i, j,'', False).replace("\t","").replace("\n", ""))
                    if stringID not in self.mStringTable:
                        self.mStringTable[stringID] = lans
                    else:
                        cv.err("String id repeat:" + str(stringID), True)
            cv.log("Loading string table OK.", True)
        except:
            cv.err("String table init failed!", True)

    def loadServerList(self, filenames):
        if self.isGMClient():
            serverlist = []
            serverNameByID = {}
            for filename in filenames:
                tb = TabFile()
                if tb.load(filename):
                    for i in xrange (tb.mRowNum):
                        serverId   = tb.get(i, 0, 0, True)
                        serverName = tb.get(i, 1,'', False).replace("\t","").replace("\n", "")
                        ip         = tb.get(i, 2, "", False).replace("\t","").replace("\n", "")
                        port       = tb.get(i, 3, 8899, True)
                        AuthIP     = tb.get(i, 4, '', False).replace("\t","").replace("\n", "")
                        isOpen     = tb.get(i, 5, 0, True)
                        status     = tb.get(i, 6, 0, True)
                        pkgurl     = tb.get(i, 7, '', False).replace("\t","").replace("\n", "")
                        Version    = tb.get(i, 8, '', False).replace("\t","").replace("\n", "")
                        Order      = tb.get(i, 9, 0, True)
                        OldsvrId   = tb.get(i, 10, 0, True)
                        if OldsvrId not in serverNameByID:
                            serverNameByID[OldsvrId] = serverName
                            serverlist.append([serverId, serverName, ip, port, AuthIP, isOpen, status, pkgurl, Version, Order, OldsvrId])
                        else:
                            cv.err("OldServerID is repeat:[%s, %s]" %(serverId, OldsvrId), True)
                            return False
            else:
                cv.err("load %s failed." %(filename), True)
                return False
            self.mServerNameByID = serverNameByID
            self.mServerList = serverlist
            self.initServerListBackupSys()
            self.correctServerListOrder()
        return True

    def loadItems(self, path):
        for root, dirs, files in os.walk(path):
            for f in files:
                filename = root + "/" + f
                if filename.endswith(".txt"):
                    configFile = open(filename, "r")
                    lines = configFile.readlines()[1:]
                    configFile.close()
                    lastpetType = ""

                    for line in lines:
                        line = line.replace("\r", "").replace("\n", "")
                        blocks = line.split("\t")
                        if f == "pet.txt":
                            petid = blocks[0]
                            petname = blocks[1].replace(" ", "")
                            petType = blocks[2].replace(" ", "")
                            self.mPetInfo[int(petid)] = str(petname)
                            self.mPetType[int(petid)] = int(petType)
                        elif f == "skillinfo.txt":
                            skillid= blocks[0]
                            skillname = blocks[1].replace(" ", "")
                            self.mSkillInfo[int(skillid)] = str(skillname)
                        elif f == "petTalent.txt":
                            petType = blocks[0]
                            petTalent = blocks[1]
                            petTalentName = blocks[3].replace(" ","")
                            if petType != lastpetType:
                                lastpetType = petType
                                self.mPetTalent[int(petType)] = {}
                                self.mPetTalent[int(petType)][int(petTalent)] = str(petTalentName)
                            else:
                                self.mPetTalent[int(petType)][int(petTalent)] = str(petTalentName)
                        elif f == "talent.txt":
                            talentid = blocks[0]
                            talentname = blocks[1].replace(" ","")
                            self.mTalentUpgrade[int(talentid)] = str(talentname)
                        elif f == "talentinvoke.txt":
                            talentid = blocks[0]
                            talentname = blocks[1].replace(" ", "")
                            self.mTalentUnlock[int(talentid)] = str(talentname)
                        else:
                            itemID = blocks[0]
                            itemName = blocks[3].replace(" ", "")
                            itemQuality = blocks[5]
                            if "未使用" not in itemName:
                                compName = self.getCompName(itemName, itemQuality)
                                self.mItemsById[int(itemID)] = compName
                                self.mItemsByName[compName] = int(itemID)
                                self.mItemQualityById[int(itemID)] = int(itemQuality)

    def getCompName(self, origin, quality):
        if int(quality) in QUALITIES:
            return "%s(%s)" %(origin, QUALITIES[int(quality)])
        return "%s(%s)" %(origin, ST("未知"))

    def initServerListBackupSys(self):
        if self.isGMClient():
            root = CONFIG_PATH + SL_BACKUP
            if not os.path.isdir(root):
                os.mkdir(root)
            for triple in os.walk(root):
                files = triple[2]
                for fn in files:
                    try:
                        key = triple[0] + "/" + fn
                        name = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(float(fn)))
                        self.mBackupFiles[key] = name
                    except:
                        cv.warn("Backup file [%s] has a error name"%(fn), True)
                        continue
                self.mSortBackup = sorted(self.mBackupFiles.iteritems(), key = lambda d:d[0])

    def backupServerList(self):
        if self.isGMClient():
            folderName = time.strftime("%Y-%m-%d", time.localtime(time.time()))
            mixPath = CONFIG_PATH + SL_BACKUP + folderName
            if not os.path.isdir(mixPath):
                os.mkdir(mixPath)
            try:
                svrlist_fhandler = open(self.mServerListFIle, "r")
                src_content = svrlist_fhandler.read()
                svrlist_fhandler.close()
                curTime = time.time()
                fn = mixPath + "/" + str(curTime)
                backup_dst_handler = open(fn, "w")
                backup_dst_handler.write(src_content)
                backup_dst_handler.close()
                viewName = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(curTime))
                self.mBackupFiles[fn] = viewName
                self.mSortBackup.append((fn,viewName,))
                cv.log("Backup ServerList Success!", True)
                return True
            except:
                cv.err("Backup ServerList Failed!", True)
                return False
        else:
            return False

    def previewRevert(self, fn):
        if self.isGMClient():
            if fn in self.mBackupFiles:
                if not self.isRevertView():
                    self.mRevertCache[0] = self.mServerList
                    self.mRevertCache[1] = self.mServerNameByID
                if self.loadServerList(fn):
                    self.mCurView = fn
                    return True
                else:
                    self.mRevertCache[0] = None
                    self.mRevertCache[1] = None
                    self.loadServerList()
        return False

    def isRevertView(self):
        return self.mRevertCache[0] != None and self.mRevertCache[1] != None

    def confirmRevert(self):
        self.mRevertCache[0] = None
        self.mRevertCache[1] = None
        cv.log("ServerList size:%s --- confirm backup" % len(self.mServerList), True)
        return self.saveServerList(True)

    def cancelRevert(self):
        self.mServerList = self.mRevertCache[0]
        self.mServerNameByID = self.mRevertCache[1]
        self.mRevertCache[0] = None
        self.mRevertCache[1] = None

    def setPolicy(self, policy):
        if policy in POLICIES:
            self.mServerListPolicy = policy

    def getSimplePolicy(self):
        if self.mServerListPolicy == SP_MANUAL:
            return SIMPLE_POLICIES[SP_CURRENCY]
        else:
            return SIMPLE_POLICIES[SP_MANUAL]

    def changeSimplePolicy(self):
        if self.mServerListPolicy == SP_MANUAL:
            self.mServerListPolicy = SP_CURRENCY
        else:
            self.mServerListPolicy = SP_MANUAL

    def updateServerList(self):
        if self.isRevertView():
            return False
        day = time.strftime('%Y%m%d')
        needSave = False
        if self.mServerListPolicy == SP_CURRENCY: # 实时策略
            for svr in self.mServerList:
                sid = svr[0]
                curol  = self.mRedisDB.get("%s:%s:cur" % (day, sid))
                curol if curol else 0
                status  = svr[6]
                for pair in STATUS_LEVEL:
                    if curol >= pair[0]:
                        status = pair[1]
                        break
                if status != svr[6]:
                    svr[6] = status
                    needSave = True
        elif self.mServerListPolicy == SP_ROLLING: # 滚服策略
            sortDict = {}
            index = 0
            for svr in self.mServerList:
                sid = svr[0]
                curol  = self.mRedisDB.get("%s:%s:cur" % (day, sid))
                curol if curol else 0
                sortDict[curol] = index
                status  = svr[6]
                for pair in STATUS_LEVEL:
                    if curol >= pair[0]:
                        status = pair[1]
                        break
                if status != svr[6]:
                    svr[6] = status
                    needSave = True
                index += 1
            try:
                sortedList = sorted(sortDict.iteritems(), key = lambda d:d[0])
                newList = []
                for svr in sortedList:
                    newList.append(self.mServerList[svr[1]])
                self.mServerList = newList
            except:
                cv.warn("Sort on ROLLING policy failed!", True)
        elif self.mServerListPolicy == SP_POPULARITY: # 人气策略
            if self.mServerList[0][6] != SS_NEW:
                self.mServerList[0][6] = SS_NEW
                needSave = True
            for idx in xrange(1, len(self.mServerList)):
                if self.mServerList[idx][6] != SS_HOT:
                    self.mServerList[idx][6] = SS_HOT
                    needSave = True
        if needSave:
            cv.log("ServerList size:%s --- policy operation" % len(self.mServerList), True)
            return self.saveServerList(True)
        else:
            return False

    def getBackupList(self):
        return self.mSortBackup

    def saveServerList(self, without_backup = False):
        if without_backup or self.backupServerList():
            contents = ["SvrID\tSvrName\tIP\tPORT\tAuthIP\tX\tX\tX\tVersion\tOrder\tOldSvrID"]
            for svrInfo in self.mServerList:
                contents.append("\n%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s" %(svrInfo[0], svrInfo[1], svrInfo[2], svrInfo[3], svrInfo[4], svrInfo[5], svrInfo[6], svrInfo[7], svrInfo[8], svrInfo[9], svrInfo[10]))
            try:
                configFile = open(self.mServerListFIle, "w")
                configFile.writelines(contents)
                configFile.close()
                return True
            except:
                cv.err("Write down serverlist failed!", True)
                return False
        else:
            return False

    def sortWithOrder(self):
        if len(self.mServerList) > 0:
            sortList = [self.mServerList[0]]
            for i in xrange(1, len(self.mServerList)):
                for j in xrange(len(sortList)):
                    src = self.mServerList[i]
                    dst = sortList[j]
                    if src[9] < dst[9]:
                        sortList.insert(j, src)
                        break
                    elif j == len(sortList) - 1:
                        sortList.append(src)
                        break
            return sortList
        else:
            return []

    def resortListWithOrder(self, reverse = False):
        sortList = self.sortWithOrder()
        newList = []
        for svr in sortList:
            newList.append(svr)
        if reverse:
            newList.reverse()
        self.mServerList = newList
        cv.log("ServerList size:%s --- resort serverlist" % len(self.mServerList), True)
        return self.saveServerList()

    def correctServerListOrder(self):
        sortList = self.sortWithOrder()
        cal = 1
        for svr in sortList:
            svr[9] = cal
            cal += 1
        cv.log("ServerList size:%s --- correct order" % len(self.mServerList), True)
        return self.saveServerList(True)

    def addServerToList(self, serverId, serverName, serverIP, serverPort, authUrl, oldServerID):
        if self.isRevertView():
            return False
        if oldServerID  not in self.mServerNameByID:
            self.mServerNameByID[oldServerID] = serverName
            self.mServerList.append([serverId, serverName, serverIP, serverPort, authUrl, 0, 4, "http://127.0.0.1/", "1", len(self.mServerList) + 1, oldServerID])
            cv.log("ServerList size:%s --- add new line" % len(self.mServerList), True)
            return self.saveServerList()
        else:
            return False

    def removeServerFromList(self, index):
        if self.isRevertView():
            return False
        if index >= 0 and index < len(self.mServerList):
            order = self.mServerList[index][9]
            del self.mServerNameByID[self.mServerList[index][10]]
            del self.mServerList[index]
            for svrInfo in self.mServerList:
                if svrInfo[9] > order:
                    svrInfo[9] -= 1
            cv.log("ServerList size:%s --- remove a line" % len(self.mServerList), True)
            return self.saveServerList()
        else:
            return False

    def openCloseServer(self, index, status):
        if self.isRevertView():
            return False
        if index >= 0 and index < len(self.mServerList) and status >= 0 and status < 2:
            self.mServerList[index][5] = status
            cv.log("ServerList size:%s --- open/close" % len(self.mServerList), True)
            return self.saveServerList(True)
        else:
            return False

    def opencloseAll(self, optype):
        if self.isRevertView():
            return False
        status = 0
        if optype == "openall":
            status = 1
        for svr in self.mServerList:
            svr[5] = status
        if len(self.mServerList) > 0:
            cv.log("ServerList size:%s --- open/close all" % len(self.mServerList), True)
            return self.saveServerList(True)
        return True

    def changeServerStateInList(self, index, status):
        if self.isRevertView():
            return False
        if index >= 0 and index < len(self.mServerList) and status > 0  and status < 6:
            self.mServerList[index][6] = status
            cv.log("ServerList size:%s --- change all status" % len(self.mServerList), True)
            return self.saveServerList()
        else:
            return False

    def moveServerInList(self, index, action):
        if self.isRevertView():
            return False
        if index >= 0 and index < len(self.mServerList):
            if action == "up":
                if index != 0:
                    tmp = self.mServerList[index]
                    self.mServerList[index] = self.mServerList[index - 1]
                    self.mServerList[index - 1] = tmp
            elif action == "top":
                if index != 0:
                    tmp = self.mServerList[index]
                    for i in xrange(index):
                        curIndex = index - i
                        self.mServerList[curIndex] = self.mServerList[curIndex - 1]
                    self.mServerList[0] = tmp
            elif action == "down":
                if index != len(self.mServerList) - 1:
                    tmp = self.mServerList[index]
                    self.mServerList[index] = self.mServerList[index + 1]
                    self.mServerList[index + 1] = tmp
            elif action == "bottom":
                if index != len(self.mServerList) - 1:
                    tmp = self.mServerList[index]
                    for i in xrange(len(self.mServerList) - 1 - index):
                        curIndex = index + i
                        self.mServerList[curIndex] = self.mServerList[curIndex + 1]
                    self.mServerList[len(self.mServerList) - 1] = tmp
            cv.log("ServerList size:%s --- move to position" % len(self.mServerList), True)
            return self.saveServerList()
        else:
            return False

    def getItemNameByID(self, itemID):
        if int(itemID) in self.mItemsById:
            return self.mItemsById[int(itemID)]
        else:
            return "u:" + str(itemID)

    def getItemIDByName(self, itemName):
        if itemName in self.mItemsByName:
            return self.mItemsByName[itemName]
        else:
            return "u:" + itemName

    def scLogtype(self, sctype):
        scid = sctype + SC_LOGTYPE * SC_BORDER
        try:
            return self.mStringTable[scid][self.mLanguage]
        except:
            return "u:" + str(scid)

    def scUseway(self, sctype):
        scid = int(sctype) + SC_USEWAY * SC_BORDER
        try:
            return self.mStringTable[scid][self.mLanguage]
        except:
            return "u:" + str(scid)

    def scGetway(self, sctype):
        scid = sctype + SC_GETWAY * SC_BORDER
        try:
            return self.mStringTable[scid][self.mLanguage]
        except:
            return "u:" + str(scid)

    def scActivity(self, sctype):
        try:
            scid = int(sctype) + SC_ACTIVITY * SC_BORDER
            return self.mStringTable[scid][self.mLanguage]
        except:
            return "u:" + str(sctype)

    def scEquippos(self, sctype):
        scid = sctype + SC_EQUIPPOS * SC_BORDER
        try:
            return self.mStringTable[scid][self.mLanguage]
        except:
            return "u:" + str(scid)

    def scTradeop(self, sctype):
        scid = sctype + SC_TRADEOP * SC_BORDER
        try:
            return self.mStringTable[scid][self.mLanguage]
        except:
            return "u:" + str(scid)

    def scRestype(self, sctype):
        scid = sctype + SC_RESTYPE * SC_BORDER
        try:
            return self.mStringTable[scid][self.mLanguage]
        except:
            return "u:" + str(scid)

    def scOperation(self, sctype):
        scid = sctype + SC_OPERATION * SC_BORDER
        try:
            return self.mStringTable[scid][self.mLanguage]
        except:
            return "u:" + str(scid)

    def scSysString(self, sctype):
        scid = sctype + SC_SYSSTRING * SC_BORDER
        try:
            return self.mStringTable[scid][self.mLanguage]
        except:
            return "u:" + str(scid)

    def scSubsistence(self, sctype):
        try:
            scid = int(sctype) + SC_SUBSISTENCE * SC_BORDER
            return self.mStringTable[scid][self.mLanguage]
        except:
            return "u:" + str(sctype)

    def scLevel(self, sctype):
        return "Lv.%s" %(sctype)

    def getGuildSetting(self, level, dtype):
        try:
            return self.mGuildLevel[level][dtype]
        except:
            return 0

Instance = ServerConfig()
