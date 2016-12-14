#coding:utf-8
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
OPTYPE_LOGINBOARD  = 1
OPTYPE_GAMEBOARD   = 2
OPTYPE_GAMEHORSE   = 3
OPTYPE_FINDINFO    = 4
OPTYPE_DEL         = 5
OPTYPE_SYSINFO     = 6

class handler_BoardOrBusy(BaseHandler):
    @authenticated
    def get(self):
        r = self.application.mCfgInfo.mRedisDB
        oldboard = r.hget("loginboard","content")
        svrNameById = self.application.mCfgInfo.mServerNameByID
        user = self.get_current_user()  
        self.render("%s/sm_boardbusy.html"%(user["op"]),loginboard=oldboard,servers = svrNameById)
    @authenticated
    def post(self):
        opType = int(self.get_body_argument("optype"))
        if opType == OPTYPE_LOGINBOARD:
            r = self.application.mCfgInfo.mRedisDB
            oldboard = r.hget("loginboard","content")
            board = self.get_body_argument("board")
            if oldboard : 
                if oldboard != board:
                    r.hset("loginboard", "content", board) 
            else:
                r.hset("loginboard", "content", board) 
            self.write("submit success")
            self.flush()
            self.finish()
        elif opType == OPTYPE_GAMEBOARD:
            svrID = self.get_body_argument("svrid")
            beginday = self.get_body_argument("beginday")
            title = self.get_body_argument("title")
            content = self.get_body_argument("content")
            begintime = time.mktime(time.strptime(beginday,'%Y-%m-%d %H:%M'))
            httpClient = zlHttpClient()
            sendData = {"UID":"", "Index":3}
            sendData["Action"] = 5
            sendData["Flag"] = 1
            sendData["LoopTime"] = 0
            sendData["ServerID"] = int(svrID)
            sendData["StartTime"] = int(begintime)
            sendData["StopTime"] = int(begintime + 3 * 12 * 30 * 86400)
            sendData["Notice"] = "%s^%s" %(title, content)
            rsltData = httpClient.sendToGM(sendData)
            self.write(rsltData)
            self.flush()
            self.finish()
        elif opType == OPTYPE_GAMEHORSE:
            svrID = self.get_body_argument("svrid")
            beginday = self.get_body_argument("beginday")
            endday = self.get_body_argument("endday")
            circle = self.get_body_argument("circle")
            content = self.get_body_argument("content")
            begintime = time.mktime(time.strptime(beginday,'%Y-%m-%d %H:%M'))
            endtime = time.mktime(time.strptime(endday,'%Y-%m-%d %H:%M'))
            httpClient = zlHttpClient()
            sendData = {"UID":"", "Index":3}
            sendData["Action"] = 5
            sendData["Flag"] = 2
            sendData["LoopTime"] = int(circle)
            sendData["ServerID"] = int(svrID)
            sendData["StartTime"] = int(begintime)
            sendData["StopTime"] = int(endtime)
            sendData["Notice"] = content
            rsltData = httpClient.sendToGM(sendData)
            self.write(rsltData)
            self.flush()
            self.finish()
        elif opType == OPTYPE_SYSINFO:
            svrID = self.get_body_argument("svrid")
            content = self.get_body_argument("content")
            httpClient = zlHttpClient()
            sendData = {"UID":"", "Index":3}
            sendData["Action"] = 5
            sendData["Flag"] = 4
            sendData["LoopTime"] = 0
            sendData["ServerID"] = int(svrID)
            sendData["StartTime"] = 0
            sendData["StopTime"] = 0
            sendData["Notice"] = content
            rsltData = httpClient.sendToGM(sendData)
            self.write(rsltData)
            self.flush()
            self.finish()
        elif opType == OPTYPE_FINDINFO:
            svrID = self.get_body_argument("svrid")
            cnttype = self.get_body_argument("cnttype")
            print svrID, cnttype
            if int(cnttype) == 1:

                sendData = {"Action":6, "ServerID":int(svrID), "Index":1,"Num":5}
                httpClient = zlHttpClient()
                rsltData = httpClient.sendToGM(sendData)
                jdata = json.loads(rsltData)
                noticeJsonArry = json.loads(jdata["data"])
                resultData = {}
                dataInfo = []
                for notice in noticeJsonArry:
                    jinfo ={}
                    jinfo["uid"] = notice['Notices']['UID']
                    jinfo["notice"] = notice['Notices']['Notice']
                    dataInfo.append(jinfo)
                resultData["listdata"] = dataInfo
                resultData["length"] = len(dataInfo)
                self.write(json.dumps(resultData))
                self.flush()
                self.finish()
            elif int(cnttype) == 2:
                sendData = {"Action":71, "ServerID":int(svrID), "StartTime":0,"StopTime":0,"Flag":1}
                httpClient = zlHttpClient()
                rsltData = httpClient.sendToGM(sendData)
                jdata = json.loads(rsltData)
                noticeJsonArry = json.loads(jdata["data"])
                resultData = {}
                dataInfo = []
                for notice in noticeJsonArry:
                    jinfo ={}
                    jinfo["uid"] = notice['Uid']
                    jinfo["notice"] = notice['Msg']
                    dataInfo.append(jinfo)
                resultData["listdata"] = dataInfo
                resultData["length"] = len(dataInfo)
                self.write(json.dumps(resultData))
                self.flush()
                self.finish()
        elif opType == OPTYPE_DEL:
            svrID = self.get_body_argument("svrid")
            cnttype = self.get_body_argument("infotype")
            uid = self.get_body_argument("uid")
            if int(cnttype) == 1:
                httpClient = zlHttpClient()
                sendData = {"UID":uid, "Index":3, "Valid":1, "Time":int(time.time())}
                sendData["Action"] = 5
                sendData["Flag"] = 1
                sendData["LoopTime"] = 0
                sendData["ServerID"] = int(svrID)
                sendData["StartTime"] = 0
                sendData["StopTime"] = 0
                sendData["Notice"] = "a^a" 
                rsltData = httpClient.sendToGM(sendData)
                self.write(rsltData)
                self.flush()
                self.finish()
            elif int(cnttype) == 2:
                httpClient = zlHttpClient()
                sendData = {"UID":uid, "Index":3, "Valid":1, "Time":int(time.time())}
                sendData["Action"] = 5
                sendData["Flag"] = 2
                sendData["LoopTime"] = 0
                sendData["ServerID"] = int(svrID)
                sendData["StartTime"] = 0
                sendData["StopTime"] = 0
                sendData["Notice"] = "a^a" 
                rsltData = httpClient.sendToGM(sendData)
                self.write(rsltData)
                self.flush()
                self.finish()

class Handler_GM_PlayerInfo(BaseHandler):
    @authenticated
    def get(self):
        svrNameById = self.application.mCfgInfo.mServerNameByID
        user = self.get_current_user()  
        self.render("%s/sm_playerinfo.html"%(user["op"]), servers = svrNameById)
    @authenticated
    def post(self):
        optype = self.get_body_argument('optype')
        if optype == "searchbase":
            svrid = int(self.get_body_argument('svrid'))
            name = self.get_body_argument('name')
            sendData = {"Action":1, "ServerID":svrid, "Name":name}
            httpClient = zlHttpClient()
            resultData = httpClient.sendToGM(sendData)
            jdata = json.loads(resultData)
            noticeJsonArry = json.loads(jdata["data"])
            resultInfo = {}
            try:
                info = noticeJsonArry[0]
                resultInfo["error"] = 0
                resultInfo["account"] = info["Account"]
                resultInfo["uuid"] = info["realName"]
                resultInfo["level"] = info["Level"]
                resultInfo["viplevel"] = info["VipLevel"]
                resultInfo["goldmoney"] = info["GoldMoney"]
                resultInfo["goldmoneypur"] = 0
                resultInfo["money"] = info["Money"]
                resultInfo["vitality"] = info["Vitality"]
                resultInfo["guild"] = info["GuildName"]
                resultInfo["channel"] = "Test"
                resultInfo["timelong"] = info["PlayedTime"]
                time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(info["LogoutTime"])))
                resultInfo["createtime"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(info["CreateTime"])))
                resultInfo["logintime"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(info["LoginTime"])))
                resultInfo["logouttime"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(info["LogoutTime"])))
                resultInfo["fbchat"] = info["Mute"]
                resultInfo["fblogin"] = info["Ban"]
            except:
                print "[ERROR]Player was not Found!"
                resultInfo["error"] = 1
            self.write(json.dumps(resultInfo))
            self.flush()
            self.finish()
        elif optype =="roleinfo":
            svrid = int(self.get_body_argument('svrid'))
            name = self.get_body_argument('name')
            sendData = {"Action":3, "ServerID":svrid, "Name":name}
            httpClient = zlHttpClient()
            resultData = httpClient.sendToGM(sendData)
            jdata = json.loads(resultData)
            dataInfo = json.loads(jdata["data"])
            roleInfo = dataInfo["Roles"]
            resultInfo = []
            rolesName = [ST("占位"),ST("棍僧"),ST("伞女"),ST("萝莉"),ST("剑客")]
            qu = [(0,0),(3,1),(6,2),(10,3),(14,4),(19,5),(25,6),(32,7),(40,8),(51,9)]
            for role in roleInfo:
                temp = {}
                    
                temp["job"] = rolesName[int(role["RoleJob"])]
                temp["info"] = ""
                temp["baoshi"] = ""
                equipInfo = role["Equipment"]
                posinfo = {}
                for data in equipInfo:
                    pos = int(data["ItemPos"])
                    itemName = self.application.mCfgInfo.mItemsById[int(data["ItemID"])]
                    if int(data["ItemStatus"]) == 1:
                        quality = ""
                        for i in xrange(len(qu)):
                            if int(data["ItemQuatify"]) >= qu[i][0]:
                                y = qu[i][1]
                                x = int(data["ItemQuatify"]) - qu[i][0]
                                quality = "%s-%s" %(y,x)
                        if pos in posinfo:
                            posinfo[pos][0] = itemName
                            posinfo[pos][1] = data["ItemLevel"]
                            posinfo[pos][2] = quality
                        else:
                            posinfo[pos] = [itemName,data["ItemLevel"],quality,""]
                    else:
                        pos = pos / 4
                        if pos in posinfo:
                            posinfo[pos][3] += "<%s>" % itemName
                        else:
                            posinfo[pos] = ["","","","<%s>" % itemName]

                for pos in posinfo:
                    temp["info"] += ST("[装备:%s]-[强化:%s]-[进阶:%s]-[宝石:%s]</br>") % (posinfo[pos][0], posinfo[pos][1], posinfo[pos][2],posinfo[pos][3])
                resultInfo.append(temp)
            self.write(json.dumps({"result":resultInfo}))
            self.flush()
            self.finish()
        elif optype =="baginfo":
            svrid = int(self.get_body_argument('svrid'))
            name = self.get_body_argument('name')
            sendData = {"Action":21, "ServerID":svrid, "Name":name}
            httpClient = zlHttpClient()
            resultData = httpClient.sendToGM(sendData)
            jdata = json.loads(resultData)
            dataInfo = json.loads(jdata["data"])
            itemData = dataInfo["Items"]
            itemInfo = "<table><tr>"
            i = 0
            for item in itemData:
                i += 1
                if i % 9 == 0:
                    if int(item["itemId"]) in self.application.mCfgInfo.mItemsById:
                        itemInfo = "%s<td>[%s-x%s]</td></tr><tr>" %(itemInfo , self.application.mCfgInfo.mItemsById[int(item["itemId"])] , item["itemNum"])
                    else:
                        itemInfo = "%s<td>[%s-x%s]</td></tr><tr>" %(itemInfo , item["itemId"] , item["itemNum"])
                else:
                    if int(item["itemId"]) in self.application.mCfgInfo.mItemsById:
                        itemInfo = "%s<td>[%s-x%s]</td>" %(itemInfo , self.application.mCfgInfo.mItemsById[int(item["itemId"])] , item["itemNum"])
                    else:
                        itemInfo = "%s<td>[%s-x%s]</td>" %(itemInfo , item["itemId"] , item["itemNum"]) 
                
            itemInfo += "</table>"   
            self.write(json.dumps({"result":itemInfo}))
            self.flush()
            self.finish()
        elif optype =="petinfo":
            svrid = int(self.get_body_argument('svrid'))
            name = self.get_body_argument('name')
            sendData = {"Action":22, "ServerID":svrid, "Name":name}
            httpClient = zlHttpClient()
            resultData = httpClient.sendToGM(sendData)
            jdata = json.loads(resultData)
            dataInfo = json.loads(jdata["data"])
            itemInfo = ""
            if len(dataInfo) == 0:
                itemData = []
                itemInfo = ST("无宠物信息")
            else:
                itemData = dataInfo["Pets"]
            petTalnet = []
            for item in itemData:
                    petTalnetstr = ""
                    if item["petTalnet"] != "":
                        petTalnet = item["petTalnet"].split(";")
                        for EachPettalnat in petTalnet:
                            each = EachPettalnat.split(",")
                            if each[0] != "":
                                petType = self.application.mCfgInfo.mPetType[item["petId"]]
                                petTalnetstr += (self.application.mCfgInfo.mPetTalent[petType][int(each[0])] + " - Lv" + each[1] +";")
                    itemInfo = ST("%s [%s:<状态:%s,阶级:%s,天赋:%s>]<br/>") %(itemInfo , self.application.mCfgInfo.mPetInfo[item["petId"]] , item["petStatus"], item["petStage"], petTalnetstr)
            self.write(json.dumps({"result":itemInfo}))
            self.flush()
            self.finish()
        elif optype == "restrict": #禁登、禁言
            svrid = int(self.get_body_argument('svrid'))
            name = self.get_body_argument('name')
            flag = int(self.get_body_argument('flag'))
            timeArr = self.get_body_argument('timelong').split("/")
            try:
                seconds = int(float(timeArr[0]) * 86400 + float(timeArr[1]) * 3600)
            except:
                seconds = -1
                print "[ERROR]Time format has some error!"
            if (flag == 0 or flag == 2) and seconds == -1:
                msg = ST("时间格式错误")
            else:
                sendData = {"Action":23, "ServerID":svrid, "Name":name, "Flag":flag, "Long":seconds}
                httpClient = zlHttpClient()
                resultData = httpClient.sendToGM(sendData)
                jdata = json.loads(resultData)
                detail = json.loads(jdata["data"])
                msg = ""
                if flag == 0:
                    msg = ST("禁言截止时间为：%s") %(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(detail["EndTime"]))))
                elif flag == 1:
                    msg = ST("禁言解除时间为：%s") %(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(detail["EndTime"]))))
                elif flag == 2:
                    msg = ST("禁登截止时间为：%s") %(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(detail["EndTime"]))))
                elif flag == 3:
                    msg = ST("禁登解除时间为：%s") %(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(detail["EndTime"]))))
            self.write(json.dumps({"result":msg}))
            self.flush()
            self.finish()
        elif optype == "friendinfo":
            svrid = int(self.get_body_argument('svrid'))
            name = self.get_body_argument('name')
            sendData = {"Action":24, "ServerID":svrid, "Name":name}
            httpClient = zlHttpClient()
            resultData = httpClient.sendToGM(sendData)
            jdata = json.loads(resultData)
            detail = json.loads(jdata["data"])
            msg = ST("<好友信息><br/>")
            try:
                total = detail["Total"]
                maxFriends = detail["Max"]
                msg += ST("好友数量：") + str(total)
                msg += "/" + str(maxFriends)
                if total > 0:
                    msg += "<br/>"
                    friendsInfo = detail["Friends"]
                    for infoData in friendsInfo:
                        info = infoData
                        msg += ST("%4s : [等级：%d]---[VIP：%d]---[公会：%s]---[战力：%d]<br/>") %(info["Name"], info["Level"], info["VipLevel"], info["GuildName"], info["BattlePoint"])
            except:
                print "[ERROR]Friends info has some error!"
                msg = ST("好友信息异常！")
            self.write(json.dumps({"result":msg}))
            self.flush()
            self.finish()

        elif optype == "guildinfo":
            svrid = int(self.get_body_argument('svrid'))
            name = self.get_body_argument('name')
            guild = self.get_body_argument('guild')
            postNames = [ST("间谍"),ST("会员"),ST("执事"),ST("长老"),ST("副会长"),ST("会长")]
            if guild == "":
                msg = ST("<公会信息><br/>无")
            else:
                sendData = {"Action":25, "ServerID":svrid, "Name":name, "Guild":guild}
                httpClient = zlHttpClient()
                resultData = httpClient.sendToGM(sendData)
                jdata = json.loads(resultData)
                detail = json.loads(jdata["data"])
                if detail:
                    try:
                        msg = ST("<公会信息>")
                        msg += ST("<br/>公会名称：") + detail["GuildName"]
                        msg += ST("<br/>公会会长：") + detail["MasterName"]
                        msg += ST("<br/>公会等级：") + str(detail["Level"])
                        msg += ST("<br/>公会经验：") + str(detail["Experience"])
                        msg += "/" + str(detail["MaxExperience"])
                        msg += ST("<br/>成员数量：") + str(detail["MemberCount"])
                        msg += "/" + str(detail["MaxMemberCount"])
                        msg += ST("<br/>玩家职位：") + postNames[detail["Post"]]
                        msg += ST("<br/>玩家贡献：") + str(detail["Meritorious"])
                        msg += "/" + str(detail["TotalMeritorious"])
                        msg += ST("<br/>公会公告：<br/>") + detail["Announcement"]
                    except:
                        print "[ERROR]Guild info has some error!"
                        msg = ST("公会信息异常！")
                else:
                    msg = ST("公会信息：无")
            self.write(json.dumps({"result":msg}))
            self.flush()
            self.finish()
        elif optype == "setvip":
            svrid = int(self.get_body_argument('svrid'))
            name = self.get_body_argument('name')
            try:
                viplevel = int(self.get_body_argument('viplevel'))
                if viplevel >= 0 and viplevel <= 15:
                    sendData = {"Action":72, "ServerID":svrid, "Name":name, "VipLevel":viplevel}
                    httpClient = zlHttpClient()
                    httpClient.sendToGM(sendData)
                    msg = ST("VIP 等级设置成功：") + str(viplevel)
                else:
                    msg = ST("VIP 等级不合法！")
            except:
                print "[ERROR] VIP format has some error!"
                msg = ST("VIP 等级格式错误！")
            self.write(json.dumps({"result":msg}))
            self.flush()
            self.finish()

        elif optype == "removegoldmoney":
            svrid = int(self.get_body_argument('svrid'))
            name = self.get_body_argument('name')
            playerGoldMoney = int(self.get_body_argument('playerGoldMoney'))
            try:
                goldmoney = int(self.get_body_argument('goldmoney'))
                if goldmoney >= 0 and goldmoney <= playerGoldMoney:
                    sendData = {"Action":26, "ServerID":svrid, "Name":name, "RemoveGoldMoney":goldmoney}
                    httpClient = zlHttpClient()
                    resultData = httpClient.sendToGM(sendData)
                    jdata = json.loads(resultData)
                    errorCode = int(jdata["errorCode"])
                    detail = json.loads(jdata["data"])
                    if errorCode == 0:
                        # msg = ST("扣除元宝成功：")
                        msg = ST("扣除元宝成功，玩家剩余元宝：") + str(detail["GoldMoney"])
                    elif errorCode == 6:
                        msg = ST("玩家已下线！")
                    else:
                        msg = ST("扣除元宝失败！")
                else:
                    msg = ST("扣除元宝数目错误！")
            except:
                print "[ERROR] RemoveGoldMoney format has some error!"
                msg = ST("金额格式错误！")
            self.write("%s"%msg)
            self.flush()
            self.finish()

        elif optype == "offline":
            svrid = int(self.get_body_argument('svrid'))
            name = self.get_body_argument('name')
            sendData = {"Action":12, "ServerID":svrid, "Name":name, "Flag":0}
            httpClient = zlHttpClient()
            httpClient.sendToGM(sendData)
            msg = str(name) + ST("踢出下线");

            self.write("%s"%msg)
            self.flush()
            self.finish()

class Handler_GM_GameMail(BaseHandler):
    @authenticated
    @coroutine
    def get(self):
        svrNameById = self.application.mCfgInfo.mServerNameByID
        items = self.application.mCfgInfo.mItemsById
        itemsQuality = self.application.mCfgInfo.mItemQualityById
        svrNameById = self.application.mCfgInfo.mServerNameByID
        user = self.get_current_user() 
        gmdb = self.application.mCfgInfo.mGMDB
        cur = yield gmdb.execute("select * from `Mails` where `Sender`='%s' AND Status = 0;" % (user['name']))
        datas = cur.fetchall()
        sendedMails = []
        for j in xrange(len(datas)):
            mail = datas[j]
            temp = []
            for i in xrange(len(mail)):
                if i == 9 :
                    temp.append(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(mail[9])))
                elif i == 10:
                    temp.append(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(mail[10])))
                elif i == 11:
                    temp.append(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(mail[11])))
                elif i == 1:
                    temp.append(svrNameById[mail[i]])
                else:
                    temp.append(mail[i])
            sendedMails.append(temp)
        color = ["2EE43E","2EE43E","2EE43E","13b1ff","13b1ff","13b1ff","AE2DE6","AE2DE6","AE2DE6","E68D2D","E68D2D","E68D2D","FF4141", "FF4141", "FF4141"]
        htmlquality = {}
        for quality in itemsQuality:
            htmlquality[quality] = color[itemsQuality[quality]]
        self.render("%s/sm_mails.html"%(user["op"]), servers = svrNameById, items = items, quality = htmlquality, sendedmails = sendedMails)

    def post(self):
        try:
            optype = self.get_body_argument('request')
            tagList = []
            if optype == "items":
                items = self.application.mCfgInfo.mItemsById
                for idx in items:
                    tagList.append("%s|%s" %(items[idx], idx))
            self.write(json.dumps({"result" : tagList}))
            self.flush()
            self.finish()
        except:
            try:
                svrid     = int(self.get_body_argument('svrid'))
                names     = self.get_body_argument('names')
                head      = self.get_body_argument('title')
                body      = self.get_body_argument('body')
                stritem   = self.get_body_argument('item')
                strres    = self.get_body_argument('res')
                toTimeStr = self.get_body_argument('totime')
                toTime    = int(time.mktime(time.strptime(toTimeStr,'%Y-%m-%d %H:%M')))
                # vlidTime  = self.get_body_argument('vlid')
                vlidStr   = self.get_body_argument('vlid')
                vlidTime  = int(time.mktime(time.strptime(vlidStr,'%Y-%m-%d %H:%M')))
                flag      = int(self.get_body_argument('flag'))
            except:
                self.write("Parameters have some errors!")
                self.flush()
                self.finish()
                return
            if svrid == -1:
                self.write("2")
                self.flush()
                self.finish()
                return
            if toTime > vlidTime:
                self.write("vlidTime have some errors!")
                self.flush()
                self.finish()
                return
            if flag == 1:
                names = ''
            tmpItems = [
                [int(value) for value in reward.split(",")]
                    for reward in stritem.split(";") if reward and reward.count(',') in (1, 2)
            ]
            tmpres = [
                [int(value) for value in reward.split(",")]
                    for reward in strres.split(";") if reward and reward.count(',') in (1, 2)
            ]
            items = ""
            ress = ""
            for temp in tmpItems:
                items = items + "%s,%s,%s;"%(temp[0], temp[1], temp[2])
            for temp in tmpres:
                ress = ress + "%s,%s;" %(temp[0], temp[1])
            user = self.get_current_user()  
            datares = [svrid, user["name"], names, head, body, items, ress, flag, toTime, vlidTime]
            self.insertMailToDB(datares)
            self.write("1")
            self.flush()
            self.finish()
    @coroutine
    def insertMailToDB(self, datares):
        gmdb = self.application.mCfgInfo.mGMDB
        yield gmdb.execute("INSERT INTO Mails ( ServerId, Sender, ToNames, MailTitle, MailBody, MailItems, MailRess, Flag, CurTime, ToTime, VlidTIme, Status ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, UNIX_TIMESTAMP(NOW()), %s, %s, 0);" , datares)

class Handler_GM_MailManage(BaseHandler):
    @authenticated
    @coroutine
    def get(self):
        gmdb = self.application.mCfgInfo.mGMDB
        cur = yield gmdb.execute("select * from `Mails` where `Status`=%d order by CurTime desc;" % (0))
        data = cur.fetchall()
        user = self.get_current_user()  
        self.render("%s/sm_mailmanage.html"%(user["op"]))
    @coroutine
    def post(self):
        gmdb = self.application.mCfgInfo.mGMDB
        optype = self.get_body_argument("optype")
        if optype == "info":
            status = int(self.get_body_argument("type"))
            svrNameById = self.application.mCfgInfo.mServerNameByID
            cur = yield gmdb.execute("select * from `Mails` where `Status`=%d order by CurTime desc;" % (status))
            datas = cur.fetchall()
            sendedMails = []
            for j in xrange(len(datas)):
                mail = datas[j]
                temp = []
                for i in xrange(len(mail)):
                    if i == 9 :
                        temp.append(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(mail[9])))
                    elif i == 10:
                        temp.append(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(mail[10])))
                    elif i == 11:
                        temp.append(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(mail[11])))
                    elif i == 1:
                        if mail[i] in svrNameById:
                            temp.append(svrNameById[mail[i]])
                        else:
                            temp.append(mail[i])
                    else:
                        temp.append(mail[i])
                sendedMails.append(temp)
            self.write(json.dumps({"mails":sendedMails}))      
            self.flush()
            self.finish()
        elif optype == "update":
            idx = int(self.get_body_argument("idx"))
            status = int(self.get_body_argument("type"))
            result = "Failed!"
            cur = yield gmdb.execute("select * from `Mails` where `MailId` = %d and `Status`= 0 order by CurTime desc;" % (idx))
            data = cur.fetchone()
            if len(data) != 0:
                if status == 1:
                    result = self.sendMailToGame(data)
                    yield gmdb.execute("UPDATE `Mails` SET `Status`=%d WHERE `MailId`=%d;" % (status, idx))
                elif status == 2:
                    result = "Success!"
                    yield gmdb.execute("UPDATE `Mails` SET `Status`=%d WHERE `MailId`=%d;" % (status, idx))
                else:
                    result = "Operation is invalid!"
            else:
                result = "Not existed!"
            self.write(result)
            self.flush()
            self.finish()

    def sendMailToGame(self, data):
        sendData = {"Action":8, "ServerID":data[1], "Name":data[3], "Flag":data[8],"Mail":"%s^%s"%(data[4], data[5]), "Items":data[6], "Res":data[7] ,"SendTime":data[10], "VlidTime":data[11]}
        httpClient = zlHttpClient()
        resultData = httpClient.sendToGM(sendData)
        jdata = json.loads(resultData)  
        return jdata

#API_KEY = "AIzaSyB3VtkN7gk1BVVJKECetZIuPp3qh9Jiuxk"
#OPEN_CLOUD_MSG = False



class Handler_GM_SendCloudMsg(BaseHandler):
    @authenticated
    def get(self):
        user = self.get_current_user()
        r = self.application.mCfgInfo.mRedisDB
        maxDevices = len(r.smembers("Client_RegisterID"))
        self.render("%s/cloud_message.html"%(user["op"]), maxDevices = maxDevices)

    @authenticated
    def post(self):
        if True:
            r = self.application.mCfgInfo.mRedisDB
            cmsg = self.get_body_argument("message")
            self.write("%s"% (self.sendToGCM(cmsg)))
            self.flush()
            self.finish()
           
    def sendToGCM(self, cloudMsg):
        url = 'https://android.googleapis.com/gcm/send'
        data = {'to':'/topics/global', 'data' : {'msg':cloudMsg} }

        responseData = ''
        for API_KEY in API_KEYS:
            headers  =  {'Content-Type' : 'application/json', 'Authorization' : 'key='+API_KEY}
            print(data)
            request  =  urllib2.Request(url, json.dumps(data), headers)
            response = urllib2.urlopen(request)
            responseData += response.read()
        if len(responseData) == 0:
            responseData = 'not got any message'
        print(responseData)
        return responseData