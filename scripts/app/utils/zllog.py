#coding:utf-8
from tornado.gen import coroutine 
class Logger:
    def __init__(self, port):
        if not os.path.exists("data/logs"):
            os.makedirs("data/logs")
        self.mLogFile = open("data/logs/log_%s" % (port), "a")
    
    def log(self, msg):
        t = time.localtime()
        try:
            self.mLogFile.write("[%04d-%02d-%02d %02d:%02d:%02d][ LOG ][Python] %s\n" % (
                t.tm_year,
                t.tm_mon,
                t.tm_mday,
                t.tm_hour,
                t.tm_min,
                t.tm_sec,
                msg
            ))
            self.mLogFile.flush()
        except:
            print_exc()

    def err(self, msg):
        t = time.localtime()
        try:
            self.mLogFile.write("[%04d-%02d-%02d %02d:%02d:%02d][ERROR][Python] %s" % (
                t.tm_year,
                t.tm_mon,
                t.tm_mday,
                t.tm_hour,
                t.tm_min,
                t.tm_sec,
                msg
            ))
            self.mLogFile.flush()
        except:
            print_exc()
