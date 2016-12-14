#coding=utf8
import datetime
from app.basehandler import BaseHandler
from traceback import print_exc

class Handler_Pay(BaseHandler):
    def get(self):
        self.application.checkPermission(self)

        r = self.application.mCfgInfo.mRedisDB
        try:
            svr = self.get_argument("svrid")
            chl = self.get_argument("t")
            acc = self.get_argument("a")
            rmb = self.get_argument("r")

            todaystr = "%s" % (datetime.date.today())
            todaystr = todaystr.replace('-', '_')

            sHeader = "pay:svr"
            cHeader = "pay:chl"
            dHeader = "pay:day"
            r.sadd(sHeader, svr)
            r.sadd(cHeader, chl)
            r.sadd(dHeader, todaystr)

            sFull = "pay:svr:%s" % (svr)
            cFull = "pay:chl:%s" % (chl)
            aFull = "pay:acc:%s" % (chl)

            olds = r.get(sFull)
            if olds == None:
                olds = 0
            else:
                olds = int(olds)
            olds += int(rmb)
            r.set(sFull, olds)

            oldc = r.get(cFull)
            if oldc == None:
                oldc = 0
            else:
                oldc = int(oldc)
            oldc += int(rmb)
            r.set(cFull, oldc)

            r.sadd(aFull, acc)

            daFull = "pay:chl:day:a:%s:%s" % (chl, todaystr)
            dpFull = "pay:chl:day:p:%s:%s" % (chl, todaystr)
            oldd = r.get(daFull)
            if oldd == None:
                oldd = 0
            else:
                oldd = int(oldd)
            oldd += int(rmb)
            r.set(daFull, oldd)
            r.sadd(dpFull, acc)

            self.write("")
            self.flush()
            self.finish()
        except:
            print_exc()