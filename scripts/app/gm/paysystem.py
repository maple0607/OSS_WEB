#coding:utf-8
from app.basehandler import BaseHandler
from tornado.web import authenticated  
from tornado.gen import coroutine
from traceback import print_exc
class Handler_GM_OrderInfo(BaseHandler):
    @authenticated
    def get(self):
        user = self.get_current_user()
        self.render("%s/sm_paysystem.html"%(user["op"]))
        
    @authenticated
    @coroutine
    def post(self):
        optype = self.get_body_argument("optype")
        opinfo = self.get_body_argument("opinfo")
        pay    = self.application.mCfgInfo.mGMDB
        result = ""
        try:
            sqlStr = "SELECT ServerId, Account, `Name`, TransactionID, FROM_UNIXTIME(PurchasedDate) FROM pay.unhandled WHERE %s LIKE '%%%s%%';" % (optype, opinfo)
            
            cur = yield pay.execute(sqlStr)
            print sqlStr
            resultData = cur.fetchall()
            print resultData
            if len(resultData) > 0:
                result +="<table class='table'><thead><tr><th>服务器ID</th><th>帐号</th><th>角色名</th><th>订单</th><th>成功时间</th></tr></thead><tbody>"
                for data in resultData:
                    result +="<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (data[0], data[1], data[2], data[3], data[4])
                result +="</tbody></table>"
            else:
                result = "尚未查询到结果"
        except:
            print_exc()
            result = "尚未查询到结果"
        self.write(result)
        self.flush()
        self.finish()
        