#coding:utf-8
from tornado.web import authenticated  
from app.basehandler import BaseHandler
import json
 
class Handler_ServerList(BaseHandler):
    @authenticated
    def get(self):
        serverlist = self.application.mCfgInfo.mServerList
        listdata = []
        index = 0
        for svr in serverlist:
            listdata.append([svr, index])
            index += 1
        user = self.get_current_user()        
        self.render("%s/serverlist.html"%(user["op"]), 
            serverlist = listdata, 
            backup = self.application.mCfgInfo.getBackupList(), 
            isPreviewRevert = self.application.mCfgInfo.isRevertView(),
            curView = self.application.mCfgInfo.mCurView,
            policy = self.application.mCfgInfo.getSimplePolicy())

    @authenticated
    def post(self):
        optype = self.get_body_argument("optype")
        sysConf = self.application.mCfgInfo
        if optype == "add":
            serverId = int(self.get_body_argument("svrid"))
            serverName = self.get_body_argument("svrname")
            serverIP = self.get_body_argument("svrip")
            serverPort = self.get_body_argument("svrport")
            authUrl = self.get_body_argument("authurl")
            oldServerID = int(self.get_body_argument("oldsvrid"))
            if sysConf.addServerToList(serverId, serverName, serverIP, serverPort, authUrl, oldServerID):
                self.write("add success refreh web page.")
            else:
                self.write("add failed refreh web page.")
            self.flush()
            self.finish()
        elif optype == "update":
            index = int(self.get_body_argument("index"))
            status = int(self.get_body_argument("status"))
            if sysConf.changeServerStateInList(index, status):
                self.write("update success refreh web page.")
            else:
                self.write("update failed refreh web page.")
            self.flush()
            self.finish()
        elif optype == "openclose":
            index = int(self.get_body_argument("index"))
            status = int(self.get_body_argument("status"))
            if sysConf.openCloseServer(index, status):
                self.write("update success refreh web page.")
            else:
                self.write("update failed refreh web page.")    
            self.flush()
            self.finish()
        elif optype == "delete":
            index = int(self.get_body_argument("index"))
            if sysConf.removeServerFromList(index):
                self.write("1")
            else:
                self.write("0")
            self.flush()
            self.finish()
        elif optype == "move":
            index = int(self.get_body_argument("index"))
            action = self.get_body_argument("action")
            if sysConf.moveServerInList(index, action):
                self.write("1")
            else:
                self.write("0")
            self.flush()
            self.finish()
        elif optype == "closeall" or optype == "openall":
            sysConf.opencloseAll(optype)
            self.write("1")
            self.flush()
            self.finish()
        elif optype == "sort":
            reverse = int(self.get_body_argument("reverse"))
            if reverse == 0:
                sysConf.resortListWithOrder()
            else:
                sysConf.resortListWithOrder(True)
            self.write("1")
            self.flush()
            self.finish()
        elif optype == "previewrevert":
            fn = self.get_body_argument("fn")
            if sysConf.previewRevert(fn):
                self.write("OK!")
            else:
                self.write("failed!")
            self.flush()
            self.finish()
        elif optype == "confirmrevert":
            if sysConf.confirmRevert():
                self.write("OK!")
            else:
                self.write("failed!")
            self.flush()
            self.finish()
        elif optype == "cancelrevert":
            if sysConf.cancelRevert():
                self.write("OK!")
            else:
                self.write("failed!")
            self.flush()
            self.finish()
        elif optype == "changesimplepolicy":
            sysConf.changeSimplePolicy()
            self.write("OK!")
            self.flush()
            self.finish()