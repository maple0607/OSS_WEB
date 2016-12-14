#coding:utf-8
from app.basehandler import *
from tornado.gen import coroutine
from tornado.web import authenticated  
import time
import hashlib
import urllib
import urllib2
from traceback import print_exc
from app.conf.stringtable import *
from app.utils.zlhttpclient import zlHttpClient
class Handler_Login(BaseHandler):
    def get(self):
        self.render("login.html", header="base3.html", error="", languages = getLanguages())
    @coroutine
    def post(self):
        #self.application.checkPermission(self)
        r = self.application.mCfgInfo.mRedisDB
        db = self.application.mCfgInfo.mGMDB
        username = self.get_argument("username", "").replace("\'", "").replace("\"", "").lower()
        password = self.get_argument("password", "")
        loginOk = False
        try:
            cur = yield db.execute("select `Username`, `Password`, `Permisson` from `Users` where `Username`='%s';" % (username))
            data = cur.fetchall()
            if len(data) == 1:
                row = data[0]
                savedPassword = row[1]
                if row[2] < 6 and row[2] > 0:
                    hashPassword = hashlib.sha1(password).hexdigest()
                    if savedPassword == hashPassword:
                        key = hashlib.sha1(str(time.time()) + username + password).hexdigest()
                        self.set_secure_cookie("user", key)
                        p = r.pipeline()
                        p.hmset("user:%s" % (key), {
                            "name": username,
                            "op": row[2],
                        })
                        p.expire("user:%s" % (key), 3600)
                        p.execute()
                        loginOk = True
        except:
            print_exc()

        yield self.gmLog(GMOP_Login, json.dumps({
            "Username": username,
            "Password": password,
            "Ok": loginOk,
        }))
        if loginOk:
            nextUrl = self.get_argument("next", "/gm/main")
            self.redirect(nextUrl)
        else:
            self.render("login.html", error="account or password is error")

class Handler_Logout(BaseHandler):
    @authenticated
    def post(self):
        r = self.application.mCfgInfo.mRedisDB
        key = self.get_secure_cookie("user")
        r.delete("user:%s"%(key))
        self.set_secure_cookie("user", "")
        self.render("login.html", header="base3.html", error="")

class Handler_AccountManage(BaseHandler):
    @authenticated
    @coroutine
    def get(self):
        user = self.get_current_user()
        db = self.application.mCfgInfo.mGMDB    
        cur = yield db.execute("select `Username`, `Password`, `Permisson` from `Users`;")
        data = cur.fetchall()
        result = []
        postss = { 1 : ST("超级管理员"), 2 : ST("运营人员"), 3 : ST("客服人员"), 4 : ST("营销人员"), 5 : ST("监控人员") }
        for acc in data:
            temp = {}
            temp["account"] = acc[0]
            temp["permession"] = postss[int(acc[2])]
            if acc[2] >= int(user["op"]):
                result.append(temp) 
        '''posts = {}  
        for i in postss:
            if i> int(user["op"]) :
                posts[i] = postss[i]'''
        self.render("%s/as_accountinfo.html"%(user["op"]), ops=postss, accs = result)

    @authenticated
    @coroutine
    def post(self):
        optype = int(self.get_body_argument("optype"))
        if optype == 1:
            account = self.get_body_argument("account")
            password = self.get_body_argument("password")
            permession = self.get_body_argument("permession")
            errMsg = ""
            if len(account) == 0 or len(password) == 0:
                errMsg = ST("帐号或密码不能为空")
            else:
                try:
                    db = self.application.mCfgInfo.mGMDB
                    password = hashlib.sha1(password).hexdigest()
                    cur = yield db.execute("insert into Users(Username, Password, Permisson) values('%s','%s',%d);" % (account, password,int(permession)))
                    data = cur.fetchall()
                except:
                    print_exc()     
                errMsg = ST("添加成功")
            self.write(errMsg)
            self.flush()
            self.finish()
        elif optype == 2:
            account = self.get_body_argument("account")
            try:
                db = self.application.mCfgInfo.mGMDB
                cur = yield db.execute("DELETE FROM Users WHERE Username = '%s'" % (account))
                data = cur.fetchall()
                print data
                errMsg = ST("处理成功")
            except:
                print_exc()     
                errMsg = ST("处理失败")
            self.write(errMsg)
            self.flush()
            self.finish()
        elif optype == 3:
            account = self.get_body_argument("account")
            password = self.get_body_argument("password")
            try:
                db = self.application.mCfgInfo.mGMDB
                password = hashlib.sha1(password).hexdigest()
                cur = yield db.execute("update Users set Password = '%s' where Username = '%s';" % (password, account))
                data = cur.fetchall()
                errMsg = ST("处理成功")
            except:
                print_exc()
                errMsg = ST("处理失败")
            self.write(errMsg)
            self.flush()
            self.finish()

class Handler_TestAccount(BaseHandler):
    @authenticated
    def get(self):
        user = self.get_current_user()
        svrNameById = self.application.mCfgInfo.mServerNameByID
        self.render("%s/test.html"%(user["op"]), servers = svrNameById)

    @authenticated
    def post(self):
        r = self.application.mCfgInfo.mRedisDB
        account = self.get_body_argument("username").lower()
        password = self.get_body_argument("password")
        if account == "" or password == "":
            msg = ST("账号和密码不能为空！")
        else:
            p = r.hget("account:" + account, "password")
            if p:
                msg = ST("密码修改成功！")
            else:
                msg = ST("账号注册成功！")
            passwordSign = hashlib.md5(password).hexdigest()
            ret = r.hset("account:" + account, "password", passwordSign)
        self.write(msg)
        self.flush()
        self.finish()

ProductToPrice = {
    "GD201512071352993" : 1100,
    "GD201512071310081" : 5500,
    "GD201512071339592" : 11000,
    "GD201512071353011" : 33000,
    "GD201512071374840" : 55000,
    "GD201512071383539" : 110000,
    "GD201512071369736" : 22000
}

class Handler_TestRecharge(BaseHandler):
    @authenticated
    def post(self):
        msg = ''
        if True:
            try:
                optype = self.get_body_argument("optype")
                svrid = int(self.get_body_argument("serverid"))
                name = self.get_body_argument("rolename")
                
                if optype == "check":
                    account = self.checkRoleExisting(svrid, name)
                    if account != "":
                        msg = "Account : %s Name : %s" %(account, name)
                    else:
                        msg = '查无此人！'
                elif optype == "recharge":
                    productId = self.get_body_argument("productid")
                    account = self.checkRoleExisting(svrid, name)
                    if account != "":
                        if productId in ProductToPrice:
                            orderSerial = self.genOrderSerial(svrid, account, name, productId, "/YWWY")
                            if self.buyProductYWWY(orderSerial, ProductToPrice[productId]):
                                msg = "订单提交成功！"
                            else:
                                msg = "订单提交失败！"
                        else:
                            msg = "Asshole!"
                    else:
                        msg = '查无此人！'
                else:
                    msg = "Invalid operation!"
            except:
                msg = "Fuck you all, motherfuker!"
        self.write(msg)
        self.flush()
        self.finish()

    def checkRoleExisting(self, svrid, name):
        sendData = {"Action" : 73, "ServerID" : svrid, "Name" : name, "Account" : '', "Type" : 1}
        httpClient = zlHttpClient()
        resultData = httpClient.sendToGM(sendData)
        jdata = json.loads(resultData)
        result = json.loads(jdata["data"])
        if int(jdata["errorCode"]) == 0 and result["QueryResult"] != "":
            return result["QueryResult"]
        else:
            return ""

    def genOrderSerial(self, serverID, account, name, productId, payType):
        try:
            name = name.encode("utf8")
        except:
            pass
        orderUrl = "%sGenOrderSerial" % (self.application.mCfgInfo.mPayServerAddr)
        orderData = {
            "account" : account,
            "name" : name,
            "serverid" : serverID,
            "productid" : productId,
            "itype" : payType,
        }
        orderSerial = urllib2.urlopen(orderUrl, urllib.urlencode(orderData)).read()
        return orderSerial

    def buyProductYWWY(self, orderSerial, money):
        payUrl = "%sYWWY" % (self.application.mCfgInfo.mPayServerAddr)
        payData = {
            "money":"%s" % (money),
            "app_order_id":orderSerial,
            "orderid":"FromGM%s" %(int(time.time()))
        }
        payRequest = urllib2.Request(payUrl, urllib.urlencode(payData))
        payResult = urllib2.urlopen(payRequest).read()
        if payResult == "SUCCESS":
            return True
        else:
            return False