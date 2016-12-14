#coding:utf-8
from app.analysis.dbhandler import *
import copy
import time

# data type
DT_Pay                    = 1
DT_ConsumeGold            = 2
DT_DailyActive            = 3
DT_CsmGoldByAct           = 4
DT_DailyCreate            = 5
DT_VipLevel               = 6
DT_Subsistence            = 7
DT_ItemSoldInMall         = 8
DT_LevelDistribution      = 9
DT_GoldMoneySurplus       = 10
DT_TotalOnlineTime        = 11
DT_CsmGoldBySys           = 12
DT_DailyCreateCountByTime = 13
DT_CurOnlineCountByTime   = 14

SessionValidTime = 300

class AnalysisMgr:
    def __init__(self):
        self.mDBHandler = None
        self.mProcHandlers = {}
        self.mDataTables = {}
        self.mLastDatas = {}
        self.mActivityNames = {}

    def startup(self, name, serverId, sqltype, user, password, host, port, dbname, charset="utf8"):
        self.mDBHandler = DBHandler(name, serverId, sqltype, user, password, host, port, dbname, charset)
        #register
        self.mProcHandlers[DT_Pay] = self.getRechargeData
        self.mDataTables[DT_Pay] = "PayData"
        self.mProcHandlers[DT_ConsumeGold] = self.getConsumeGoldData
        self.mDataTables[DT_ConsumeGold] = "ConsumeGold"
        self.mProcHandlers[DT_DailyActive] = self.getDailyActiveData
        self.mDataTables[DT_DailyActive] = "DailyActive"
        self.mProcHandlers[DT_CsmGoldByAct] = self.getConsumeGoldByActData
        self.mDataTables[DT_CsmGoldByAct] = "ConsumeGoldByAct"
        self.mProcHandlers[DT_DailyCreate] = self.getDailyCreateData
        self.mDataTables[DT_DailyCreate] = "DailyCreate"
        self.mProcHandlers[DT_VipLevel] = self.getVipLevelData
        self.mDataTables[DT_VipLevel] = "VipLevel"
        self.mProcHandlers[DT_Subsistence] = self.getSubsistence
        self.mDataTables[DT_Subsistence] = "Subsistence"
        self.mProcHandlers[DT_ItemSoldInMall] = self.getItemSoldInMall
        self.mDataTables[DT_ItemSoldInMall] = "ItemSoldInMall"
        self.mProcHandlers[DT_LevelDistribution] = self.getLevelDistribution
        self.mDataTables[DT_LevelDistribution] = "LevelDistribution"
        self.mProcHandlers[DT_GoldMoneySurplus] = self.getGoldMoneySurplus
        self.mDataTables[DT_GoldMoneySurplus] = "GoldMoneySurplus"
        self.mProcHandlers[DT_TotalOnlineTime] = self.getTotalOnlineTime
        self.mDataTables[DT_TotalOnlineTime] = "TotalOnlineTime"
        self.mProcHandlers[DT_CsmGoldBySys] = self.getConsumeGoldBySysData
        self.mDataTables[DT_CsmGoldBySys] = "ConsumeGoldBySys"
        self.mProcHandlers[DT_DailyCreateCountByTime] = self.getDCCountByTimeData
        self.mDataTables[DT_DailyCreateCountByTime] = "DailyCreateCountByTime"
        self.mProcHandlers[DT_CurOnlineCountByTime] = self.getCOCountByTimeData
        self.mDataTables[DT_CurOnlineCountByTime] = "CurOnlineCountByTime"

    def getActivityName(self, actId):
        if actId in self.mActivityNames:
            return self.mActivityNames[actId];
        else:
            return actId

    def getData(self, dType, beginTime, endTime):
        if self.mDBHandler:
            if dType in self.mProcHandlers and dType in self.mDataTables:
                sqlStr = "select * from %s where Date >= %s and Date < %s"%(self.mDataTables[dType], beginTime, endTime)
                if dType not in self.mLastDatas:
                    typeData = [beginTime, endTime, time.time(), {}]
                    self.mLastDatas[dType] = typeData
                    result = self.mDBHandler.executeSql(sqlStr)
                    typeData[3] = self.mProcHandlers[dType](result, beginTime, endTime)
                else:
                    typeData = self.mLastDatas[dType]
                    requery = False
                    if typeData[0] != beginTime or typeData[1] != endTime:
                        requery = True
                    elif time.time() - typeData[2] > SessionValidTime:
                        requery = True

                    if requery:
                        typeData = [beginTime, endTime, time.time(), {}]
                        self.mLastDatas[dType] = typeData
                        result = self.mDBHandler.executeSql(sqlStr)
                        typeData[3] = self.mProcHandlers[dType](result, beginTime, endTime)
                return typeData[3]

    def getRechargeData(self, result, beginTime, endTime):
        anaResult = {}
        total = [0, 0, 0]
        byServerId = {}
        byDate = {}
        for line in result:
            date      = line[0]
            serverId  = line[1]
            totalGold = line[2]
            count     = line[3]
            accCount  = line[4]

            #total
            total[0] += totalGold
            total[1] += count
            total[2] += accCount

            #date
            if date not in byDate:
                byDate[date] = [[0, 0, 0], {}]
            dateData = byDate[date]
            totalOfDate = dateData[0]
            totalOfDate[0] += totalGold
            totalOfDate[1] += count
            totalOfDate[2] += accCount
            dateData[1][serverId] = [totalGold, count, accCount]

            #serverid
            if serverId not in byServerId:
                byServerId[serverId] = [[0, 0, 0], {}]
            dateData = byServerId[serverId]
            totalOfDate = dateData[0]
            totalOfDate[0] += totalGold
            totalOfDate[1] += count
            totalOfDate[2] += accCount
            dateData[1][date] = [totalGold, count, accCount]

        anaResult["Total"] = total
        anaResult["ByDate"] = byDate
        anaResult["ByServerId"] = byServerId
        return anaResult

    def getConsumeGoldData(self, result, beginTime, endTime):
        anaResult = {}
        total = [0]
        byServerId = {}
        byDate = {}
        for line in result:
            date      = line[0]
            serverId  = line[1]
            count     = line[2]

            #total
            total[0] += count
            
            #date
            if date not in byDate:
                byDate[date] = [[0], {}]
            dateData = byDate[date]
            dateData[0][0] += count
            dateData[1][serverId] = [count]

            #serverid
            if serverId not in byServerId:
                byServerId[serverId] = [[0], {}]
            dateData = byServerId[serverId]
            dateData[0][0] += count
            dateData[1][date] = [count]

        anaResult["Total"] = total
        anaResult["ByDate"] = byDate
        anaResult["ByServerId"] = byServerId
        return anaResult

    def getDailyActiveData(self, result, beginTime, endTime):
        anaResult = {}
        total = [0]
        byServerId = {}
        byDate = {}
        for line in result:
            date      = line[0]
            serverId  = line[1]
            count     = line[2]

            #total
            total[0] += count
            
            #date
            if date not in byDate:
                byDate[date] = [[0], {}]
            dateData = byDate[date]
            dateData[0][0] += count
            dateData[1][serverId] = [count]

            #serverid
            if serverId not in byServerId:
                byServerId[serverId] = [[0], {}]
            dateData = byServerId[serverId]
            dateData[0][0] += count
            dateData[1][date] = [count]

        anaResult["Total"] = total
        anaResult["ByDate"] = byDate
        anaResult["ByServerId"] = byServerId
        return anaResult

    def getConsumeGoldByActData(self, result, beginTime, endTime):
        anaResult = {}
        total = {}
        byServerId = {}
        byDate = {}
        for line in result:
            date        = line[0]
            serverId    = line[1]
            dataPairs   = line[2].split(";")
            dataByActId = {}
            for pair in dataPairs:
                key_value = pair.split(":")
                if len(key_value) == 2:
                    dataByActId[key_value[0]] = int(key_value[1])

            #total
            for key in dataByActId:
                if key not in total:
                    total[key] = dataByActId[key]
                else:
                    total[key] += dataByActId[key]

            #date
            if date not in byDate:
                byDate[date] = [{}, {}]
            dateData = byDate[date]
            totalOfDate = dateData[0]
            for key in dataByActId:
                if key not in totalOfDate:
                    totalOfDate[key] = dataByActId[key]
                else:
                    totalOfDate[key] += dataByActId[key]
            dateData[1][serverId] = copy.deepcopy(dataByActId)

            #serverid
            if serverId not in byServerId:
                byServerId[serverId] = [{}, {}]
            dateData = byServerId[serverId]
            totalOfServ = dateData[0]
            for key in dataByActId:
                if key not in totalOfServ:
                    totalOfServ[key] = dataByActId[key]
                else:
                    totalOfServ[key] += dataByActId[key]
            dateData[1][date] = copy.deepcopy(dataByActId)

        anaResult["Total"] = total
        anaResult["ByDate"] = byDate
        anaResult["ByServerId"] = byServerId
        return anaResult

    def getDailyCreateData(self, result, beginTime, endTime):
        anaResult = {}
        total = [0]
        byServerId = {}
        byDate = {}
        for line in result:
            date      = line[0]
            serverId  = line[1]
            count     = line[2]

            #total
            total[0] += count
            
            #date
            if date not in byDate:
                byDate[date] = [[0], {}]
            dateData = byDate[date]
            dateData[0][0] += count
            dateData[1][serverId] = [count]

            #serverid
            if serverId not in byServerId:
                byServerId[serverId] = [[0], {}]
            dateData = byServerId[serverId]
            dateData[0][0] += count
            dateData[1][date] = [count]

        anaResult["Total"] = total
        anaResult["ByDate"] = byDate
        anaResult["ByServerId"] = byServerId
        return anaResult

    def getVipLevelData(self, result, beginTime, endTime):
        anaResult = {}
        total = []
        byServerId = {}
        byDate = {}
        for line in result:
            date       = line[0]
            serverId   = line[1]
            vipCounts  = line[2].split(";")

            #total
            for i in xrange(len(vipCounts)):
                if i < len(total):
                    total[i] += int(vipCounts[i])
                else:
                    if vipCounts[i] != '':
                        total.append(int(vipCounts[i]))

            #date
            if date not in byDate:
                byDate[date] = [[], {}]
            dateData = byDate[date]
            counts = dateData[0]
            for i in xrange(len(vipCounts)):
                if i < len(counts):
                    counts[i] += int(vipCounts[i])
                else:
                    if vipCounts[i] != '':
                        counts.append(int(vipCounts[i]))
            dateData[1][serverId] = [int(value) for value in vipCounts if value != '']

            #serverid
            if serverId not in byServerId:
                byServerId[serverId] = [[], {}]
            dateData = byServerId[serverId]
            counts = dateData[0]
            for i in xrange(len(vipCounts)):
                if i < len(counts):
                    counts[i] += int(vipCounts[i])
                else:
                    if vipCounts[i] != '':
                        counts.append(int(vipCounts[i]))
            dateData[1][date] = [int(value) for value in vipCounts  if value != '']

        anaResult["Total"] = total
        anaResult["ByDate"] = byDate
        anaResult["ByServerId"] = byServerId
        return anaResult

    def getSubsistence(self, result, beginTime, endTime):
        anaResult = {}
        total = {}
        byServerId = {}
        byDate = {}

        for line in result:
            date        = line[0]
            serverId    = line[1]
            dataPairs   = line[2].split(";")
            dataBySubType = {}
            result = self.mDBHandler.executeSql("select Count from DailyCreate where Date = %s and ServerID = %s" %(date,serverId))
            try:
                baseActive = int(result[0][0])
            except:
                baseActive = 1
            for pair in dataPairs:
                key_value = pair.split(":")
                if len(key_value) == 2:
                    dataBySubType[key_value[0]] = int(key_value[1])
            dataBySubType["1"] = baseActive

            #total
            for key in dataBySubType:
                if key not in total:
                    total[key] = dataBySubType[key]
                else:
                    total[key] += dataBySubType[key]

            #date
            if date not in byDate:
                byDate[date] = [{}, {}]
            dateData = byDate[date]
            totalOfDate = dateData[0]
            for key in dataBySubType:
                if key not in totalOfDate:
                    totalOfDate[key] = dataBySubType[key]
                else:
                    totalOfDate[key] += dataBySubType[key]
            dateData[1][serverId] = copy.deepcopy(dataBySubType)

            #serverid
            if serverId not in byServerId:
                byServerId[serverId] = [{}, {}]
            dateData = byServerId[serverId]
            totalOfServ = dateData[0]
            for key in dataBySubType:
                if key not in totalOfServ:
                    totalOfServ[key] = dataBySubType[key]
                else:
                    totalOfServ[key] += dataBySubType[key]
            dateData[1][date] = copy.deepcopy(dataBySubType)

        anaResult["Total"] = total
        anaResult["ByDate"] = byDate
        anaResult["ByServerId"] = byServerId
        return anaResult

    def getItemSoldInMall(self, result, beginTime, endTime):
        anaResult = {}
        total = {}
        byServerId = {}
        byDate = {}
        for line in result:
            date        = line[0]
            serverId    = line[1]
            dataPairs   = line[2].split(";")
            dataByActId = {}
            for pair in dataPairs:
                key_value = pair.split(":")
                if len(key_value) == 2:
                    dataByActId[key_value[0]] = int(key_value[1])

            #total
            for key in dataByActId:
                if key not in total:
                    total[key] = dataByActId[key]
                else:
                    total[key] += dataByActId[key]

            #date
            if date not in byDate:
                byDate[date] = [{}, {}]
            dateData = byDate[date]
            totalOfDate = dateData[0]
            for key in dataByActId:
                if key not in totalOfDate:
                    totalOfDate[key] = dataByActId[key]
                else:
                    totalOfDate[key] += dataByActId[key]
            dateData[1][serverId] = copy.deepcopy(dataByActId)

            #serverid
            if serverId not in byServerId:
                byServerId[serverId] = [{}, {}]
            dateData = byServerId[serverId]
            totalOfServ = dateData[0]
            for key in dataByActId:
                if key not in totalOfServ:
                    totalOfServ[key] = dataByActId[key]
                else:
                    totalOfServ[key] += dataByActId[key]
            dateData[1][date] = copy.deepcopy(dataByActId)

        anaResult["Total"] = total
        anaResult["ByDate"] = byDate
        anaResult["ByServerId"] = byServerId
        return anaResult

    def getLevelDistribution(self, result, beginTime, endTime):
        anaResult = {}
        total = {}
        byServerId = {}
        byDate = {}
        for line in result:
            date        = line[0]
            serverId    = line[1]
            dataPairs   = line[2].split(";")
            dataByActId = {}
            for pair in dataPairs:
                key_value = pair.split(":")
                if len(key_value) == 2:
                    dataByActId[key_value[0]] = int(key_value[1])

            #total
            for key in dataByActId:
                if key not in total:
                    total[key] = dataByActId[key]
                else:
                    total[key] += dataByActId[key]

            #date
            if date not in byDate:
                byDate[date] = [{}, {}]
            dateData = byDate[date]
            totalOfDate = dateData[0]
            for key in dataByActId:
                if key not in totalOfDate:
                    totalOfDate[key] = dataByActId[key]
                else:
                    totalOfDate[key] += dataByActId[key]
            dateData[1][serverId] = copy.deepcopy(dataByActId)

            #serverid
            if serverId not in byServerId:
                byServerId[serverId] = [{}, {}]
            dateData = byServerId[serverId]
            totalOfServ = dateData[0]
            for key in dataByActId:
                if key not in totalOfServ:
                    totalOfServ[key] = dataByActId[key]
                else:
                    totalOfServ[key] += dataByActId[key]
            dateData[1][date] = copy.deepcopy(dataByActId)

        anaResult["Total"] = total
        anaResult["ByDate"] = byDate
        anaResult["ByServerId"] = byServerId
        return anaResult

    def getGoldMoneySurplus(self, result, beginTime, endTime):
        anaResult = {}
        total = [0]
        byServerId = {}
        byDate = {}
        for line in result:
            date      = line[0]
            serverId  = line[1]
            count     = line[2]

            #total
            total[0] += count
            
            #date
            if date not in byDate:
                byDate[date] = [[0], {}]
            dateData = byDate[date]
            dateData[0][0] += count
            dateData[1][serverId] = [count]

            #serverid
            if serverId not in byServerId:
                byServerId[serverId] = [[0], {}]
            dateData = byServerId[serverId]
            dateData[0][0] += count
            dateData[1][date] = [count]

        anaResult["Total"] = total
        anaResult["ByDate"] = byDate
        anaResult["ByServerId"] = byServerId
        return anaResult

    def getTotalOnlineTime(self, result, beginTime, endTime):
        anaResult = {}
        total = [0]
        byServerId = {}
        byDate = {}
        for line in result:
            date      = line[0]
            serverId  = line[1]
            count     = line[2]

            #total
            total[0] += count
            
            #date
            if date not in byDate:
                byDate[date] = [[0], {}]
            dateData = byDate[date]
            dateData[0][0] += count
            dateData[1][serverId] = [count]

            #serverid
            if serverId not in byServerId:
                byServerId[serverId] = [[0], {}]
            dateData = byServerId[serverId]
            dateData[0][0] += count
            dateData[1][date] = [count]

        anaResult["Total"] = total
        anaResult["ByDate"] = byDate
        anaResult["ByServerId"] = byServerId

        return anaResult

    def getConsumeGoldBySysData(self, result, beginTime, endTime):
        anaResult = {}
        total = {}
        byServerId = {}
        byDate = {}
        for line in result:
            date        = line[0]
            serverId    = line[1]
            dataPairs   = line[2].split(";")
            dataBySysId = {}
            for pair in dataPairs:
                key_value = pair.split(":")
                if len(key_value) == 2:
                    dataBySysId[key_value[0]] = int(key_value[1])

            #total
            for key in dataBySysId:
                if key not in total:
                    total[key] = dataBySysId[key]
                else:
                    total[key] += dataBySysId[key]

            #date
            if date not in byDate:
                byDate[date] = [{}, {}]
            dateData = byDate[date]
            totalofDate = dateData[0]
            for key in dataBySysId:
                if key not in totalofDate:
                    totalofDate[key] = dataBySysId[key]
                else:
                    totalofDate[key] += dataBySysId[key]
            dateData[1][serverId] = copy.deepcopy(dataBySysId)

            #serverid
            if serverId not in byServerId:
                byServerId[serverId] = [{}, {}]
            dateData = byServerId[serverId]
            totalOfServ = dateData[0]
            for key in dataBySysId:
                if key not in totalOfServ:
                    totalOfServ[key] = dataBySysId[key]
                else:
                    totalOfServ[key] += dataBySysId[key]
            dateData[1][date] = copy.deepcopy(dataBySysId)

        anaResult["Total"] = total
        anaResult["ByDate"] = byDate
        anaResult["ByServerId"] = byServerId
        return anaResult

    def getDCCountByTimeData(self, result, beginTime, endTime):
        anaResult = {}
        total = []
        byServerId = {}
        byDate = {}
        for line in result:
            date       = line[0]
            serverId   = line[1]
            dcCounts  = line[2].split(";")

            #total
            for i in xrange(len(dcCounts)):
                if i < len(total):
                    total[i] += int(dcCounts[i])
                else:
                    if dcCounts[i] != '':
                        total.append(int(dcCounts[i]))

            #date
            if date not in byDate:
                byDate[date] = [[], {}]
            dateData = byDate[date]
            counts = dateData[0]
            for i in xrange(len(dcCounts)):
                if i < len(counts):
                    counts[i] += int(dcCounts[i])
                else:
                    if dcCounts[i] != '':
                        counts.append(int(dcCounts[i]))
            dateData[1][serverId] = [int(value) for value in dcCounts if value != '']

            #serverid
            if serverId not in byServerId:
                byServerId[serverId] = [[], {}]
            dateData = byServerId[serverId]
            counts = dateData[0]
            for i in xrange(len(dcCounts)):
                if i < len(counts):
                    counts[i] += int(dcCounts[i])
                else:
                    if dcCounts[i] != '':
                        counts.append(int(dcCounts[i]))
            dateData[1][date] = [int(value) for value in dcCounts  if value != '']

        anaResult["Total"] = total
        anaResult["ByDate"] = byDate
        anaResult["ByServerId"] = byServerId
        return anaResult

    def getCOCountByTimeData(self, result, beginTime, endTime):
        anaResult = {}
        total = []
        byServerId = {}
        byDate = {}
        for line in result:
            date       = line[0]
            serverId   = line[1]
            coCounts  = line[2].split(";")

            #total
            for i in xrange(len(coCounts)):
                if i < len(total):
                    total[i] += int(coCounts[i])
                else:
                    if coCounts[i] != '':
                        total.append(int(coCounts[i]))

            #date
            if date not in byDate:
                byDate[date] = [[], {}]
            dateData = byDate[date]
            counts = dateData[0]
            for i in xrange(len(coCounts)):
                if i < len(counts):
                    counts[i] += int(coCounts[i])
                else:
                    if coCounts[i] != '':
                        counts.append(int(coCounts[i]))
            dateData[1][serverId] = [int(value) for value in coCounts if value != '']

            #serverid
            if serverId not in byServerId:
                byServerId[serverId] = [[], {}]
            dateData = byServerId[serverId]
            counts = dateData[0]
            for i in xrange(len(coCounts)):
                if i < len(counts):
                    counts[i] += int(coCounts[i])
                else:
                    if coCounts[i] != '':
                        counts.append(int(coCounts[i]))
            dateData[1][date] = [int(value) for value in coCounts  if value != '']

        anaResult["Total"] = total
        anaResult["ByDate"] = byDate
        anaResult["ByServerId"] = byServerId
        return anaResult


AnaMgr = AnalysisMgr()