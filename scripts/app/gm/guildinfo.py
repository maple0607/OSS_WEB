#encoding:utf8
import time
import json
import datetime
import copy
import urllib
import urllib2
from app.basehandler import BaseHandler
from app.utils.zlhttpclient import zlHttpClient
from tornado.web import authenticated  
from tornado.gen import coroutine
from app.conf.stringtable import *
from app.conf.conf import *

TitlesGuild = [
ST("公会名称"),
ST("公会会长"),
ST("公会等级"),
ST("公会公告")
]

GuildKeys = [
"GuildName",
"Master",
"GuildLevel",
"Announce"
]

PlayerTitles = [
ST("账号"),
ST("角色名"),
ST("职位"),
ST("等级"),
ST("VIP"),
ST("可用贡献"),
ST("总贡献"),
]

PlayerKeys = [
"Account",
"PlayerName",
"Post",
"PlayerLevel",
"VipLevel",
"Meritorious",
"TotalMeritorious"
]

PostNames = [ST("间谍"),ST("会员"),ST("执事"),ST("长老"),ST("副会长"),ST("会长")]

class Handler_GM_GuildInfo(BaseHandler):
    @authenticated
    def get(self):
        svrNameById = self.application.mCfgInfo.mServerNameByID
        user = self.get_current_user()  
        self.render("%s/guildinfo.html"%(user["op"]), servers=svrNameById)

    @authenticated
    def post(self):
        svrid = int(self.get_body_argument('svrid'))
        guildname = self.get_body_argument('guildname')
        sendData = {"Action":28, "ServerID":svrid, "GuildName":guildname}
        httpClient = zlHttpClient()
        resultData = httpClient.sendToGM(sendData)
        jdata = json.loads(resultData)
        dataInfo = json.loads(jdata["data"])

        # guild info
        verTitle = "<table class='table table-striped table-bordered table-hover table-condensed'><head><tr>"
        for title in TitlesGuild:
            verTitle += "<th>" + title + "</th>"
        verTitle += "<th>" + ST("公会建设度") + "</th>"
        verTitle += "<th>" + ST("公会人数") + "</th>"
        verTitle += "</tr></head><body>"

        if dataInfo and dataInfo[0]:
            for key in GuildKeys:
                if key in dataInfo[0]:
                    verTitle += "<td>%s</td>" % (dataInfo[0][key]) 
                else:
                    verTitle += "<td>NULL</td>"
            baseMember = 0
            baseExp = 0
            curMember = 0
            if "GuildLevel" in dataInfo[0]:
                baseExp = Instance.getGuildSetting(dataInfo[0]["GuildLevel"], 0)
            if "GuildExp" in dataInfo[0]:
                curMember = dataInfo[0]["GuildExp"]
            verTitle += "<td>%s/%s</td>" % (curMember, baseExp)
            if "GuildLevel" in dataInfo[0]:
                baseMember = Instance.getGuildSetting(dataInfo[0]["GuildLevel"], 1)
            verTitle += "<td>%s/%s</td>" % (len(dataInfo), baseMember)
        verTitle += "</body></table><div class='clearfix'/>"

        # player info
        verTitle += "<table class='table table-striped table-bordered table-hover table-condensed'><head><tr>"
        for title in PlayerTitles:
            verTitle += "<th>" + title + "</th>"
        verTitle += "</tr></head><body>"

        for row in dataInfo:
            for key in PlayerKeys:
                if key in row:
                    if key == 'Post':
                        verTitle += "<td>%s</td>" % (PostNames[row[key]])
                    else:
                        verTitle += "<td>%s</td>" % (row[key]) 
                else:
                    verTitle += "<td>NULL</td>"
            verTitle += "</tr>"
        verTitle += "</body></table><div class='clearfix'/>"

        self.write(verTitle)
        self.flush()
        self.finish()