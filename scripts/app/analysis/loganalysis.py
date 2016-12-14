#coding:utf-8
import time
import json
import datetime
from app.basehandler import BaseHandler
from app.utils.zlhttpclient import zlHttpClient
from tornado.web import authenticated
from app.analysis.analysismanager import *
from app.conf.conf import *
from app.conf.stringtable import *

GRAPH_TPYES = {
    1 : ST("3D柱状"),
    2 : ST("区域线性"),
    3 : ST("平面柱状"),
    4 : ST("普通线性"),
}

PAY_DATA_TYEP = {
    1 : ST("充值金额"),
    2 : ST("充值次数"),
    3 : ST("充值人数"),
}

COLLECTIONS = {
    1 : ST("按日期-类型汇总"),
    2 : ST("按区服-类型汇总"),
    3 : ST("按类型-区服汇总"),
    4 : ST("按类型-日期汇总"),
}

OPT_3D = {
    "enabled" : True,
    "alpha" : 10,
    "beta" : 20,
    "depth" : 70,
}

STANDARDS = {
    1 : ST("用服务做为参数"),
    2 : ST("用时间做为参数")
}

MAX_LEVEL = 165

def getTimeWithTCount(count):
    count += 1
    count *= 5
    return "%.2d:%.2d" % (int(count / 60), int(count % 60))

class HighchartsData:
    def __init__(self):
        pass

    def formatTimeStamp(self, ts, dFormat = "%m-%d"):
        return time.strftime(dFormat, time.localtime(ts))

    def getBaseOption(self, style, titles, tss):
        base = {}
        if style == 1:
            base["chart"] = {"type" : "column", "options3d" : OPT_3D}
        elif style == 2:
            base["chart"] = {"type" : "area"}
        elif style == 3:
            base["chart"] = {"type" : "column"}
        else:
            base["chart"] = {}

        base["chart"]["zoomType"] = "x"
        base["chart"]["resetZoomButton"] = { "position" : { "y" : -30 } }
        base["chart"]["panning"] = True
        base["chart"]["panKey"] = "shift"
        base["title"] = {"text" : titles[0]}
        base["subtitle"] = {"text" : titles[1]}

        if style == 1:
            base["plotOptions"] = {"column" : {"depth" : 70, "stacking" : "normal"}}

        dateStr = []
        for ts in tss:
            dateStr.append(self.formatTimeStamp(ts))
        if style == 1 or style == 3:
            dateStr.append(ST("总量"))
        base["xAxis"] = {"categories" : dateStr}
        base["yAxis"] = {"title" : {"text" : titles[2]}}
        base["tooltip"] = {"valueSuffix" : titles[3]}
        return base

    def getDataByIndex(self, style, titles, tss, data, index = 0):
        base = self.getBaseOption(style, titles, tss)
        base["tooltip"]["pointFormat"] = '<b style="color:{series.color}">{series.name}</b><b>:{point.y}</b><br/>%s:{point.per:.2f}%' %(ST("比重"))

        #series
        series = []
        sortData = {}
        totalData = []
        dataByServerID = data["ByServerId"]
        for sid in dataByServerID:
            if sid not in sortData:
                sortData[sid] = []
       
        dataByDate = data["ByDate"]
        count = 0
        for ts in tss:
            if ts in dataByDate:
                totalOfDate = dataByDate[ts][0]
                dataByServerID = dataByDate[ts][1]
                for sid in sortData:
                    if sid not in dataByServerID:
                        sortData[sid].append([0, 0.0])
                    else:
                        val = dataByServerID[sid][index]
                        sortData[sid].append([val, 100.0 * val / totalOfDate[index]])
                totalData.append([totalOfDate[index], 100.0])
            else:
                for sid in sortData:
                    sortData[sid].append([0, 0.0])
                totalData.append([0, 0.0])
            count += 1

        for sid in sortData:
            if style == 1 or style == 3:
                val = data["ByServerId"][sid][0][index]
                sortData[sid].append([val, 100.0 * val / data["Total"][index]])
            nativeData = sortData[sid]
            seriesData = []
            for pair in nativeData:
                seriesData.append({"y" : pair[0], "per" : pair[1]})
            series.append({"name" : sid, "data" : seriesData})
        seriesTotal = []
        if style == 1 or style == 3:
            totalData.append([data["Total"][index], 100.0])
        for pair in totalData:
            seriesTotal.append({"y" : pair[0], "per" : pair[1]})
        series.append({"name" : ST("总量"), "data" : seriesTotal})
        base["series"] = series
        return base

    def getDataByIndexDD(self, style, titles, tss, data, index = 0, baseCate = 1):
        base = self.getBaseOption(style, titles, tss)
        base["tooltip"]["pointFormat"] = '<b style="color:{series.color}">[{series.name}]</b><b>:{point.y}</b><br/>%s:{point.per:.2f}%%' %(ST("比重"))
        base["xAxis"] = {"type": 'category'}

        #series
        drilldown = { "series" : [] }
        total = data["Total"][index]
        dataBySid = data["ByServerId"]
        dataByDate = data["ByDate"]

        # total
        totSeries = { "name" : "Total", "data" : [] }
        if total > 0:
            if baseCate == 1: # 以ServerID为基本单位
                ddid = "Every-Server-Total"
                drillOfServer = { "name" : ddid, "id" : ddid, "data" : [] }
                drilldown["series"].append(drillOfServer)
                for sid in dataBySid:
                    sData = dataBySid[sid]
                    sTotData = sData[0][index]
                    sDateData = sData[1]
                    if sTotData > 0:
                        drillOfServer["data"].append({ "name" : sid, "y" : sTotData, "drilldown" : sid, "per" : 100.0 * sTotData / total })
                        drillOfDate = { "name" : "%s Every-Date-Total" % (sid), "id" : sid, "data" : [] }
                        drilldown["series"].append(drillOfDate)

                        for ts in tss:
                            date = self.formatTimeStamp(ts)
                            if ts in sDateData:
                                value = sDateData[ts][index]
                                drillOfDate["data"].append({ "name" : date, "y" : value, "per" : 100.0 * value / sTotData })
                            else:
                                drillOfDate["data"].append({ "name" : date, "y" : 0, "per" : 0.0 })
            else: # 以Date为基本单位
                ddid = "Every-Date-Total"
                drillOfDate = { "name" : ddid, "id" : ddid, "data" : [] }
                drilldown["series"].append(drillOfDate)
                for ts in tss:
                    date = self.formatTimeStamp(ts)
                    if ts in dataByDate:
                        dData = dataByDate[ts]
                        dTotData = dData[0][index]
                        dSerData = dData[1]
                        if dTotData > 0:
                            drillOfDate["data"].append({ "name" : date, "y" : dTotData, "drilldown" : ts, "per" : 100.0 * dTotData / total })
                            drillOfServer = { "name" : "%s Every-Server-Total" % (date), "id" : ts, "data" : [] }
                            drilldown["series"].append(drillOfServer)
                            for sid in dSerData:
                                value = dSerData[sid][index]
                                drillOfServer["data"].append({ "name" : sid, "y" : value, "per" : 100.0 * value / dTotData })
                    else:
                        drillOfDate["data"].append({ "name" : date, "y" : 0, "per" : 0.0 })
            totSeries["data"].append({ "name" : "Total", "y" : total, "drilldown" : ddid, "per" : 100.0})
        else:
            totSeries["data"].append({ "name" : "Total", "y" : total, "drilldown" : None, "per" : 0.0})
        base["series"] = [totSeries,]
        base["drilldown"] = drilldown
        return base

    def getComplexDataWithDictDD(self, style, titles, tss, data, nameConvt):
        base = self.getBaseOption(style, titles, tss)
        base["tooltip"]["pointFormat"] = '<b style="color:{series.color}">[{point.name}][{series.name}]</b><b>:{point.y}</b><br/>%s:{point.per:.2f}%%' %(ST("比重"))
        base["xAxis"] = {"type": 'category'}

        #series
        series = []
        drilldown = { "series" : [] }
        dataBySid = data["ByServerId"]
        dataByDate = data["ByDate"]
        for sid in dataBySid:
            nsrs = { "name" : sid, "data" : [] }
            dData = dataBySid[sid][1]
            for ts in tss:
                date = self.formatTimeStamp(ts)
                if ts in dData:
                    did = "[%s][%s]" %(date, sid)
                    cateTotal = dataByDate[ts][0]
                    dTotal = 0
                    for cid in cateTotal:
                        dTotal += cateTotal[cid]
                    cates = dData[ts]
                    cTotal = 0
                    drillData = { "name" : did, "id" : did, "data" : [] }
                    for cid in cates:
                        cTotal += cates[cid]
                    for cid in cates:
                        drillData["data"].append({ "name" : nameConvt(cid), "y" : cates[cid], "per" : 100.0 * cates[cid] / cTotal })
                    drilldown["series"].append(drillData)
                    nsrs["data"].append({ "name" : date, "y" : cTotal, "drilldown" : did, "per" : 100.0 * cTotal / dTotal})
                else:
                    nsrs["data"].append({ "name" : date, "y" : 0, "drilldown" : None })
            series.append(nsrs)

        base["series"] = series
        base["drilldown"] = drilldown
        return base

    def getComplexDataWithList(self, style, titles, tss, data, collection, nameConvt = None):
        base = self.getBaseOption(style, titles, tss)
        #series
        series = []
        totalData = data["Total"]
        if collection == 1 or collection == 2:
            itemTotal = []
            for item in totalData:
                itemTotal.append([])
            if collection == 1:
                dataByDate = data["ByDate"]
                for ts in tss:
                    if ts in dataByDate:
                        dData = dataByDate[ts][0]
                        for i in xrange(len(itemTotal)):
                            if i < len(dData):
                                itemTotal[i].append(dData[i])
                            else:
                                itemTotal[i].append(0)
                    else:
                        for lst in itemTotal:
                            lst.append(0)
            elif collection == 2:
                dataByServerID = data["ByServerId"]
                serverIds = []
                for sid in dataByServerID:
                    serverIds.append(sid)
                    sData = dataByServerID[sid][0]
                    for i in xrange(len(itemTotal)):
                        if i < len(sData):
                            itemTotal[i].append(sData[i])
                        else:
                            itemTotal[i].append(0)
                if style == 1 or style == 3:
                    serverIds.append(ST("总量"))
                base["xAxis"] = {"categories" : serverIds}
            if style == 1 or style == 3:
                for i in xrange(len(itemTotal)):
                    itemTotal[i].append(totalData[i])
            for i in xrange(len(itemTotal)):
                if nameConvt:
                    series.append({"name" : nameConvt(i), "data" : itemTotal[i]})
                else:
                    series.append({"name" : str(i), "data" : itemTotal[i]})
        elif collection == 3 or collection == 4:
            itemList = []
            for i in xrange(len(totalData)):
                if nameConvt:
                    itemList.append(nameConvt(i))
                else:
                    itemList.append(i)
            if collection == 3:
                dataByServerID = data["ByServerId"]
                for sid in dataByServerID:
                    series.append({"name" : sid, "data" : dataByServerID[sid][0]})
            elif collection == 4:
                dataByDate = data["ByDate"]
                for date in dataByDate:
                    series.append({"name" : time.strftime("%Y-%m-%d", time.localtime(date)), "data" : dataByDate[date][0]})
            base["xAxis"] = {"categories" : itemList}
        base["series"] = series
        return base

    def makeSubsistenceToGraph(self, style, titles, tss, data, nameConvt):
        base = self.getBaseOption(style, titles, tss)
        base["xAxis"] = {"type": 'category'}

        #series
        series = []
        drilldown = { "series" : [] }
        dataBySid = data["ByServerId"]
        dataByDate = data["ByDate"]
        sortDataType = ["2", "3", "7", "15", "30"]
        for ts in tss:
            if ts in dataByDate:
                dateStr = self.formatTimeStamp(ts)
                nsrs = { "name" : dateStr, "data" : [] }
                sTotData = dataByDate[ts][0]
                sDataBySid = dataByDate[ts][1]
                drillData = { "name" : dateStr, "id" : dateStr, "data" : [] }
                for sid in sDataBySid:
                    dsData = sDataBySid[sid]
                    firstDayCount = dsData["1"]
                    if firstDayCount > 0:
                        for st in sortDataType:
                            per = float("%.2f" % (100.0 * dsData[st] / firstDayCount))
                            drillData["data"].append({ "name" : "[%s][%s]" %(sid, nameConvt(st)), "y" : per, "drilldown" : None})
                drilldown["series"].append(drillData)
                firstDayCount = sTotData["1"]
                if firstDayCount > 0:
                    for st in sortDataType:
                        per = float("%.2f" % (100.0 * sTotData[st] / firstDayCount))
                        nsrs["data"].append({ "name" : nameConvt(st), "y" : per, "drilldown" : dateStr})
                    series.append(nsrs)

        base["series"] = series
        base["drilldown"] = drilldown
        return base

    def makeSubsistenceToForm(self, tss, data):
        sortDataType = ["2", "3", "7", "15", "30"]
        verTitle = "<table class='table table-striped table-bordered table-hover table-condensed'><head><tr><th>%s</th><th>+1day</th><th>+2day</th><th>+6day</th><th>+14day</th><th>+29day</th></tr></head><body>" %(ST("日期"))
        dataByDate = data["ByDate"]
        for ts in tss:
            if ts in dataByDate:
                dTotData = dataByDate[ts][0]
                verTitle += "<tr><td>%s</td>" % (time.strftime("%Y-%m-%d", time.localtime(ts)))
                for dt in sortDataType:
                    if dTotData["1"] == 0:
                        verTitle += "<td></td>"
                    else:
                        per = 100.0 * dTotData[dt] / dTotData["1"]
                        if per <= 0.00001:
                            verTitle += "<td></td>"
                        else:
                            verTitle += "<td>%d | %.2f%%</td>" % (dTotData[dt], per)
                verTitle += "</tr>"
        verTitle += "</body></table><div class='clearfix'/>"

        return verTitle

    def makeLevelDistributionToGraph(self, style, titles, tss, data, nameConvt):
        base = self.getBaseOption(style, titles, tss)
        base["xAxis"] = {"type": 'category'}

        #series
        series = []
        drilldown = { "series" : [] }
        dataBySid = data["ByServerId"]
        dataByDate = data["ByDate"]
        for sid in dataBySid:
            nsrs = { "name" : sid, "data" : [] }
            dData = dataBySid[sid][1]
            for ts in tss:
                date = self.formatTimeStamp(ts)
                if ts in dData:
                    did = "[%s][%s]" %(date, sid)
                    cateTotal = dataByDate[ts][0]
                    dTotal = 0
                    for cid in cateTotal:
                        dTotal += cateTotal[cid]
                    cates = dData[ts]
                    cTotal = 0
                    drillData = { "name" : did, "id" : did, "data" : [] }
                    for cid in cates:
                        cTotal += cates[cid]
                    for i in xrange(1, MAX_LEVEL+1):
                        cid = str(i)
                        if cid in cates:
                            drillData["data"].append({ "name" : nameConvt(cid), "y" : cates[cid]})
                        else:
                            drillData["data"].append({ "name" : nameConvt(cid), "y" : 0})
                    drilldown["series"].append(drillData)
                    nsrs["data"].append({ "name" : date, "y" : cTotal, "drilldown" : did})
                else:
                    nsrs["data"].append({ "name" : date, "y" : 0, "drilldown" : None })
            series.append(nsrs)

        base["series"] = series
        base["drilldown"] = drilldown
        return base

    def checkTimeValid(self, beginStr, endStr, result = []):
        startTime = time.mktime(time.strptime(beginStr, "%Y-%m-%d"))
        endTime = time.mktime(time.strptime(endStr, "%Y-%m-%d"))
        days = (endTime - startTime) / 86400
        if days < 1:
            return False
        elif days > 30:
            endTime = startTime +  86400 * 30
        result.append(startTime)
        result.append(endTime)
        dates = []
        while startTime < endTime:
            dates.append(startTime)
            startTime += 86400
        result.append(dates)
        return True

    def makeComplexDataToForm(self, tss, data):
        verTitle = "<table class='table table-striped table-bordered table-hover table-condensed'><head><tr><th>%s</th>"%(ST("服务器"))
        for ts in tss:
            verTitle += "<th>"+self.formatTimeStamp(ts, "%Y/%m/%d")+"</th>"
        verTitle += "</tr></head><body>"

        dataBySid = data["ByServerId"]
        SortSid = sorted(dataBySid)
        dataByDate = data["ByDate"]

        for sid in SortSid:
            dData = dataBySid[sid][1]
            verTitle += "<tr><td>%s</td>" % (str(sid))
            for ts in tss:
                if ts in dData:
                    cateTotal = dData[ts]
                    dTotal = 0
                    for cid in cateTotal:
                        dTotal += cateTotal[cid]
                    verTitle +="<td>%s</td>"%(str(dTotal))
                else:
                    verTitle += "<td></td>"
            verTitle += "</tr>"

        verTitle += "<tr><td>total</td>"
        for ts in tss:
            if ts in dataByDate:
                cateTotal = dataByDate[ts][0]
                dTotal = 0
                for cid in cateTotal:
                    dTotal += cateTotal[cid]
                verTitle += "<td>%s</td>"%(str(dTotal))
            else:
                verTitle += "<td></td>"
        verTitle += "</tr>"

        verTitle += "</body></table><div class='clearfix'/>"
        return verTitle


    def makeDataByIndexToForm(self, tss, data, index = 0):
        verTitle = "<table class='table table-striped table-bordered table-hover table-condensed'><head><tr><th>%s</th>" % (ST("服务器"))
        for ts in tss:
            verTitle += "<th>" + self.formatTimeStamp(ts, "%Y/%m/%d") + "</th>"
        verTitle += "</tr></head><body>"

        dataBySid = data["ByServerId"]
        SortSid = sorted(dataBySid)
        dataByDate = data["ByDate"]

        for sid in SortSid:
            dData = dataBySid[sid][1]
            verTitle += "<tr><td>%s</td>" % (str(sid))
            for ts in tss:
                if ts in dData:
                    verTitle += "<td>%s</td>" % (str(dData[ts][index]))
                else:
                    verTitle += "<td></td>"
            verTitle += "</tr>"

        verTitle += "<tr><td>total</td>"
        for ts in tss:
            if ts in dataByDate:
                cateTotal = dataByDate[ts][0]
                verTitle += "<td>%s</td>"%(str(cateTotal[index]))
            else:
                verTitle += "<td></td>"
        verTitle += "</tr>"

        verTitle += "</body></table><div class='clearfix'/>"
        return verTitle

    def makeComplexDataWithListToForm(self, tss, data, nameConvert = None):
        verTitle = "<table class='table table-striped table-bordered table-hover table-condensed'><head><tr><th>%s</th>" % (ST("服务器"))
        totalData = data["Total"]
        if nameConvert:
            for i in xrange(len(totalData)):
                verTitle += "<th>" + nameConvert(i) + "</th>"
        else:
            for i in xrange(len(totalData)):
                verTitle += "<th>" + str(i) + "</th>"
        verTitle += "</tr></head><body>"

        dataBySid = data["ByServerId"]
        SortSid = sorted(dataBySid)
        for sid in SortSid:
            dData = dataBySid[sid][0]
            verTitle += "<tr><td>%s</td>" % (str(sid))
            for i in range(0, len(dData)):
                if dData[i] == 0:
                    verTitle += "<td></td>"
                else:
                    verTitle += "<td>%s</td>" % (str(dData[i]))
            verTitle += "</tr>"
        verTitle += "</body></table><div class='clearfix'/>"
        return verTitle

    def makeLevelDistributionToForm(self, tss, data):
        verTitle = "<table class='table table-striped table-bordered table-hover table-condensed'><head><tr><th>%s</th>" % (ST("服务器"))
        for i in xrange(1, MAX_LEVEL + 1):
            verTitle += "<th>" + str(i) + "</th>"
        verTitle += "</tr></head><body>"

        dataBySid = data["ByServerId"]
        SortSid = sorted(dataBySid)
        for sid in SortSid:
            dData = dataBySid[sid][1]
            for ts in tss:
                verTitle += "<tr><td>%s</td>" % (str(sid)+" : "+self.formatTimeStamp(ts, "%Y/%m/%d"))
                if ts in dData:
                    level_every = dData[ts]
                    for i in xrange(1, MAX_LEVEL + 1):
                        if str(i) in level_every.keys():
                            verTitle += "<td>%s</td>" % (str(level_every[str(i)]))
                        else:
                            verTitle += "<td></td>"
                else:
                    for i in xrange(1, MAX_LEVEL + 1):
                        verTitle += "<td></td>"
                verTitle += "</tr>"
        verTitle += "</body></table><div class='clearfix'/>"
        return verTitle


class Handler_LA_Pay(BaseHandler):
    @authenticated
    def get(self):
        user = self.get_current_user()
        self.render("%s/la_pay.html"%(user["op"]), styles = GRAPH_TPYES, dataTypes = PAY_DATA_TYEP, standards = STANDARDS)

    def post(self):
        beginstr = self.get_body_argument('bgntime')
        endstr = self.get_body_argument('endtime')
        style = int(self.get_body_argument('style'))
        dataType = int(self.get_body_argument('dataType'))
        standard = int(self.get_body_argument('standard'))
        result = {"ok" : False, "count" : {}}
        getResult = []
        if HighchartsData().checkTimeValid(beginstr, endstr, getResult):
            result["ok"] = True
            data = AnaMgr.getData(1, getResult[0], getResult[1])
            titles = [PAY_DATA_TYEP[dataType], ST("服/天")]
            if dataType == 1:
                titles.append(ST("单位") + "：" + ST("元宝"))
                titles.append(ST("元宝"))
            elif dataType == 2:
                titles.append(ST("单位") + "：" + ST("单"))
                titles.append(ST("单"))
            else:
                titles.append(ST("单位") + "：" + ST("人"))
                titles.append(ST("人"))
            if style == -1:
                result["content"] = HighchartsData().makeDataByIndexToForm(getResult[2], data, dataType - 1)
            else:
                result["count"] = HighchartsData().getDataByIndexDD(style, titles, getResult[2], data, dataType - 1, standard)
        self.write(json.dumps({"result":result}))
        self.flush()
        self.finish()

class Handler_LA_ConsumeGold(BaseHandler):
    @authenticated
    def get(self):
        user = self.get_current_user()
        self.render("%s/la_consumegold.html"%(user["op"]), styles = GRAPH_TPYES, standards = STANDARDS)

    def post(self):
        beginstr = self.get_body_argument('bgntime')
        endstr = self.get_body_argument('endtime')
        style = int(self.get_body_argument('style'))
        standard = int(self.get_body_argument('standard'))
        result = {"ok" : False, "count" : {}}
        getResult = []
        if HighchartsData().checkTimeValid(beginstr, endstr, getResult):
            data = AnaMgr.getData(2, getResult[0], getResult[1])
            result["ok"] = True
            if style == -1:
                result["content"] = HighchartsData().makeDataByIndexToForm(getResult[2], data, 0)
            else:
                result["count"] = HighchartsData().getDataByIndexDD(style, [ST("元宝消耗总值"), ST("服/天"), ST("单位") + "：" + ST("元宝"), ST("元宝")], getResult[2], data, 0, standard)
        self.write(json.dumps({"result":result}))
        self.flush()
        self.finish()

class Handler_LA_DailyActive(BaseHandler):
    @authenticated
    def get(self):
        user = self.get_current_user()
        self.render("%s/la_dailyactive.html"%(user["op"]), styles = GRAPH_TPYES, standards = STANDARDS)

    def post(self):
        beginstr = self.get_body_argument('bgntime')
        endstr = self.get_body_argument('endtime')
        style = int(self.get_body_argument('style'))
        standard = int(self.get_body_argument('standard'))
        result = {"ok" : False, "count" : {}}
        getResult = []
        if HighchartsData().checkTimeValid(beginstr, endstr, getResult):
            data = AnaMgr.getData(3, getResult[0], getResult[1])
            result["ok"] = True
            if style == -1:
                result["content"] = HighchartsData().makeDataByIndexToForm(getResult[2], data, 0)
            else:
                result["count"] = HighchartsData().getDataByIndexDD(style, [ST("日活跃总值"), ST("服/天"), ST("单位") + "：" + ST("人"), ST("人")], getResult[2], data, 0, standard)
        self.write(json.dumps({"result":result}))
        self.flush()
        self.finish()

class Handler_LA_ConsumeGoldByAct(BaseHandler):
    @authenticated
    def get(self):
        user = self.get_current_user()
        self.render("%s/la_consumegoldbyact.html"%(user["op"]), styles = GRAPH_TPYES, collections = COLLECTIONS)

    def post(self):
        beginstr = self.get_body_argument('bgntime')
        endstr = self.get_body_argument('endtime')
        style = int(self.get_body_argument('style'))
        result = {"ok" : False, "count" : {}}
        getResult = []
        if HighchartsData().checkTimeValid(beginstr, endstr, getResult):
            data = AnaMgr.getData(4, getResult[0], getResult[1])
            result["ok"] = True
            if style == -1:
                result["content"] = HighchartsData().makeComplexDataToForm(getResult[2],data)
            else:
                result["count"] = HighchartsData().getComplexDataWithDictDD(style, [ST("每日活动消耗"), ST("服/天"), ST("单位") + "：" + ST("元宝"), ST("元宝")], getResult[2], data, Instance.scActivity)
        self.write(json.dumps({"result":result}))
        self.flush()
        self.finish()

class Handler_LA_DailyCreate(BaseHandler):
    @authenticated
    def get(self):
        user = self.get_current_user()
        self.render("%s/la_dailycreate.html"%(user["op"]), styles = GRAPH_TPYES, standards = STANDARDS)

    def post(self):
        beginstr = self.get_body_argument('bgntime')
        endstr = self.get_body_argument('endtime')
        style = int(self.get_body_argument('style'))
        standard = int(self.get_body_argument('standard'))
        result = {"ok" : False, "count" : {}}
        getResult = []
        if HighchartsData().checkTimeValid(beginstr, endstr, getResult):
            data = AnaMgr.getData(5, getResult[0], getResult[1])
            result["ok"] = True
            if style == -1:
                result["content"] = HighchartsData().makeDataByIndexToForm(getResult[2], data, 0)
            else:
                result["count"] = HighchartsData().getDataByIndexDD(style, [ST("日创角总值"), ST("服/天"), ST("单位") + "：" + ST("人"), ST("人")], getResult[2], data, 0, standard)
        self.write(json.dumps({"result":result}))
        self.flush()
        self.finish()

class Handler_LA_VipLevel(BaseHandler):
    @authenticated
    def get(self):
        user = self.get_current_user()
        self.render("%s/la_viplevel.html"%(user["op"]), styles = GRAPH_TPYES, collections = COLLECTIONS)

    def post(self):
        beginstr = self.get_body_argument('bgntime')
        startTime = time.mktime(time.strptime(beginstr, "%Y-%m-%d"))
        endstr = time.strftime("%Y-%m-%d", time.localtime(startTime + 86400))
        # endstr = self.get_body_argument('endtime')
        style = int(self.get_body_argument('style'))
        collection = int(self.get_body_argument('collection'))
        result = {"ok" : False, "count" : {}}
        getResult = []
        if HighchartsData().checkTimeValid(beginstr, endstr, getResult):
            data = AnaMgr.getData(6, getResult[0], getResult[1])
            result["ok"] = True
            if style == -1:
                result["content"] = HighchartsData().makeComplexDataWithListToForm(getResult[2], data)
            else:
                result["count"] = HighchartsData().getComplexDataWithList(style, [ST("每日VIP统计"), ST("服/天"), ST("单位") + "：" + ST("人"), ST("人")], getResult[2], data, collection)
        self.write(json.dumps({"result":result}))
        self.flush()
        self.finish()

class Handler_LA_Subsistence(BaseHandler):
    @authenticated
    def get(self):
        user = self.get_current_user()
        self.render("%s/la_subsistence.html"%(user["op"]), styles = GRAPH_TPYES, collections = COLLECTIONS)

    def post(self):
        beginstr = self.get_body_argument('bgntime')
        endstr = self.get_body_argument('endtime')
        style = int(self.get_body_argument('style'))
        result = {"ok" : False, "count" : {}}
        getResult = []
        if HighchartsData().checkTimeValid(beginstr, endstr, getResult):
            data = AnaMgr.getData(7, getResult[0], getResult[1])
            result["ok"] = True
            if style == -1:
                result["content"] = HighchartsData().makeSubsistenceToForm(getResult[2], data)
            else:
                result["count"] = HighchartsData().makeSubsistenceToGraph(style, [ST("留存情况分析"), ST("服/天"), ST("单位") + "：" + "%", "%"], getResult[2], data, Instance.scSubsistence)
        self.write(json.dumps({"result":result}))
        self.flush()
        self.finish()

class Handler_LA_ItemSoldInMall(BaseHandler):
    @authenticated
    def get(self):
        user = self.get_current_user()
        self.render("%s/la_itemsoldinmall.html"%(user["op"]), styles = GRAPH_TPYES, collections = COLLECTIONS)

    def post(self):
        beginstr = self.get_body_argument('bgntime')
        endstr = self.get_body_argument('endtime')
        style = int(self.get_body_argument('style'))
        result = {"ok" : False, "count" : {}}
        getResult = []
        if HighchartsData().checkTimeValid(beginstr, endstr, getResult):
            data = AnaMgr.getData(8, getResult[0], getResult[1])
            result["ok"] = True
            if style == -1:
                result["content"] = HighchartsData().makeComplexDataToForm(getResult[2],data)
            else:
                result["count"] = HighchartsData().getComplexDataWithDictDD(style, [ST("商城道具售卖"), ST("服/天"), ST("单位") + "：" + ST("个"), ST("个")], getResult[2], data, Instance.getItemNameByID)
        self.write(json.dumps({"result":result}))
        self.flush()
        self.finish()

class Handler_LA_LevelDistribution(BaseHandler):
    @authenticated
    def get(self):
        user = self.get_current_user()
        self.render("%s/la_leveldistribution.html"%(user["op"]), styles = GRAPH_TPYES, collections = COLLECTIONS)

    def post(self):
        beginstr = self.get_body_argument('bgntime')
        startTime = time.mktime(time.strptime(beginstr, "%Y-%m-%d"))
        endstr = time.strftime("%Y-%m-%d", time.localtime(startTime + 86400))
        # endstr = self.get_body_argument('endtime')
        style = int(self.get_body_argument('style'))
        result = {"ok" : False, "count" : {}}
        getResult = []
        if HighchartsData().checkTimeValid(beginstr, endstr, getResult):
            data = AnaMgr.getData(9, getResult[0], getResult[1])
            result["ok"] = True
            if style == -1:
                result["content"] = HighchartsData().makeLevelDistributionToForm(getResult[2],data)
            else:
                result["count"] = HighchartsData().makeLevelDistributionToGraph(style, [ST("等级分布"), ST("服/天"), ST("单位") + "：" + ST("人"), ST("人")], getResult[2], data, Instance.scLevel)
        self.write(json.dumps({"result":result}))
        self.flush()
        self.finish()

class Handler_LA_GoldMoneySurplus(BaseHandler):
    @authenticated
    def get(self):
        user = self.get_current_user()
        self.render("%s/la_goldmoneysurplus.html"%(user["op"]), styles = GRAPH_TPYES, standards = STANDARDS)

    def post(self):
        beginstr = self.get_body_argument('bgntime')
        endstr = self.get_body_argument('endtime')
        style = int(self.get_body_argument('style'))
        standard = int(self.get_body_argument('standard'))
        result = {"ok" : False, "count" : {}}
        getResult = []
        if HighchartsData().checkTimeValid(beginstr, endstr, getResult):
            data = AnaMgr.getData(10, getResult[0], getResult[1])
            result["ok"] = True
            if style == -1:
                result["content"] = HighchartsData().makeDataByIndexToForm(getResult[2], data, 0)
            else:
                result["count"] = HighchartsData().getDataByIndexDD(style, [ST("元宝库存"), ST("服/天"), ST("单位") + "：" + ST("元宝"), ST("元宝")], getResult[2], data, 0, standard)
        self.write(json.dumps({"result":result}))
        self.flush()
        self.finish()

class Handler_LA_TotalOnlineTime(BaseHandler):
    @authenticated
    def get(self):
        user = self.get_current_user()
        self.render("%s/la_totalonlinetime.html"%(user["op"]), styles = GRAPH_TPYES, standards = STANDARDS)

    def post(self):
        beginstr = self.get_body_argument('bgntime')
        endstr = self.get_body_argument('endtime')
        style = int(self.get_body_argument('style'))
        standard = int(self.get_body_argument('standard'))
        result = {"ok" : False, "count" : {}}
        getResult = []
        if HighchartsData().checkTimeValid(beginstr, endstr, getResult):
            data = AnaMgr.getData(11, getResult[0], getResult[1])
            result["ok"] = True
            if style == -1:
                result["content"] = HighchartsData().makeDataByIndexToForm(getResult[2], data, 0)
            else:
                result["count"] = HighchartsData().getDataByIndexDD(style, [ST("在线时长"), ST("服/天"), ST("单位") + "：" + ST("秒"), ST("秒")], getResult[2], data, 0, standard)
        self.write(json.dumps({"result":result}))
        self.flush()
        self.finish()

class Handler_LA_ConsumeGoldBySys(BaseHandler):
    @authenticated
    def get(self):
        user = self.get_current_user()
        self.render("%s/la_consumegoldbysys.html"%(user["op"]), styles = GRAPH_TPYES, collections = COLLECTIONS)

    def post(self):
        beginstr = self.get_body_argument('bgntime')
        endstr = self.get_body_argument('endtime')
        style = int(self.get_body_argument('style'))
        result = {"ok" : False, "count" : {}}
        getResult = []
        if HighchartsData().checkTimeValid(beginstr, endstr, getResult):
            data = AnaMgr.getData(12, getResult[0], getResult[1])
            result["ok"] = True
            if style == -1:
                result["content"] = HighchartsData().makeComplexDataToForm(getResult[2],data)
            else:
                result["count"] = HighchartsData().getComplexDataWithDictDD(style, [ST("每日系统消耗"), ST("服/天"), ST("单位") + "：" + ST("元宝"), ST("元宝")], getResult[2], data, Instance.scUseway)
        self.write(json.dumps({"result":result}))
        self.flush()
        self.finish()

class Handler_LA_DailyCreateCountByTime(BaseHandler):
    @authenticated
    def get(self):
        user = self.get_current_user()
        self.render("%s/la_dccountbytime.html"%(user["op"]), styles = GRAPH_TPYES, collections = COLLECTIONS)

    def post(self):
        beginstr = self.get_body_argument('bgntime')
        startTime = time.mktime(time.strptime(beginstr, "%Y-%m-%d"))
        endstr = time.strftime("%Y-%m-%d", time.localtime(startTime+86400))
        style = int(self.get_body_argument('style'))
        collection = int(self.get_body_argument('collection'))
        result = {"ok" : False, "count" : {}}
        getResult = []
        if HighchartsData().checkTimeValid(beginstr, endstr, getResult):
            data = AnaMgr.getData(13, getResult[0], getResult[1])
            result["ok"] = True
            if style == -1:
                result["content"] = HighchartsData().makeComplexDataWithListToForm(getResult[2], data, getTimeWithTCount)
            else:
                result["count"] = HighchartsData().getComplexDataWithList(style, [ST("每日新增分布统计"), ST("服/天"), ST("单位") + "：" + ST("人"), ST("人")], getResult[2], data, collection, getTimeWithTCount)
        self.write(json.dumps({"result":result}))
        self.flush()
        self.finish()

class Handler_LA_CurOnlineCountByTime(BaseHandler):
    @authenticated
    def get(self):
        user = self.get_current_user()
        self.render("%s/la_cocountbytime.html"%(user["op"]), styles = GRAPH_TPYES, collections = COLLECTIONS)

    def post(self):
        beginstr = self.get_body_argument('bgntime')
        startTime = time.mktime(time.strptime(beginstr, "%Y-%m-%d"))
        endstr = time.strftime("%Y-%m-%d", time.localtime(startTime+86400))
        # endstr = self.get_body_argument('endtime')
        style = int(self.get_body_argument('style'))
        collection = int(self.get_body_argument('collection'))
        result = {"ok" : False, "count" : {}}
        getResult = []
        if HighchartsData().checkTimeValid(beginstr, endstr, getResult):
            data = AnaMgr.getData(14, getResult[0], getResult[1])
            result["ok"] = True
            if style == -1 or collection == -1:
                result["content"] = HighchartsData().makeComplexDataWithListToForm(getResult[2], data, getTimeWithTCount)
            else:
                result["count"] = HighchartsData().getComplexDataWithList(style, [ST("每日在线分布统计"), ST("服/天"), ST("单位") + "：" + ST("人"), ST("人")], getResult[2], data, collection, getTimeWithTCount)
        self.write(json.dumps({"result":result}))
        self.flush()
        self.finish()