#coding:utf-8
import json
from app.basehandler import BaseHandler
from tornado.web import authenticated 
from app.utils.zlhttpclient import zlHttpClient
class Handler_ServerDebug(BaseHandler):
    @authenticated
    def get(self):
        svrNameById = self.application.mCfgInfo.mServerNameByID
        user = self.get_current_user()
        self.render("%s/serverdebug.html"%(user["op"]), servers = svrNameById)
    @authenticated
    def post(self):
        svrid = self.get_body_argument("svrid")
        content = self.get_body_argument("content")
        sendData = {}
        sendData["Action"] = 105
        sendData["ServerID"] = int(svrid)
        sendData["Data"] = content
        httpClient = zlHttpClient()
        rsltData = httpClient.sendToGM(sendData)
        jdata = json.loads(rsltData)
        self.write(jdata["data"])
        self.flush()
        self.finish()       