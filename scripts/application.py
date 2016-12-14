#coding=utf8
import os
import sys
import thread
import tornado.web
import __builtin__
from tornado_mysql import pools
from traceback import print_exc
from app.conf.conf import Instance
from urls import handlers, gmhandlers
from app.utils.views import *

reload(sys)
sys.setdefaultencoding('utf-8')

class Application(tornado.web.Application):
    def __init__(self, port):
        cv.log("Application init...", True)
        cv.log("Server start on [http://0.0.0.0:" + str(port) + "]", True)
        self.mPort = port
        self.mCfgInfo = Instance.startup("configs/main.json", self.mPort)

        settings = dict(
            template_path = os.path.join(os.path.dirname(__file__), "../templates"),
            static_path = os.path.join(os.path.dirname(__file__), "../static"),
            debug = self.mCfgInfo.mIsDebug,
            cookie_secret = "N141c78MRsKESllCkcXADffqR5vSZEk7rRU5EUv78LQ=",
            xsrf_cookies = False,
            login_url = "/gm/login",
        )

        if int(port) == 8888:
            tornado.web.Application.__init__(self, gmhandlers, **settings)
        else:
            tornado.web.Application.__init__(self, handlers, **settings)
        self.listen(port)

    def checkPermission(self, handler):
        if "X-Forwarded-For" in handler.request.headers:
            remote_ip = handler.request.headers["X-Forwarded-For"]
        else:
            remote_ip = handler.request.remote_ip
        permissionIP = self.mCfgInfo.mPermissionIP
        result = True
        if len(permissionIP) > 0:
            if remote_ip not in permissionIP:
                result = False
                for ipAddress in permissionIP:
                    if remote_ip.startswith(ipAddress):
                        result = True
                        break
        if not result:
            raise tornado.web.HTTPError(403, "permission denied")

applicaton = None