#coding=utf8

import json
import redis
import urllib2
import cPickle
import hashlib
import base64
import socket
import time
from traceback import *
API_KEYS = [
    'AIzaSyAkQVjqwfvX2QylRg3918f-Blpol4D9R-U',
    'AIzaSyD3IzQY-Xhpiizh9QBmmyhDxb2kC9GtBvw',
    'AIzaSyDWr4un86SeKpHKT9Gi-jIwQmlfUm_GXHg',
]
def sendGCM(cloudMsg):
    url = 'https://android.googleapis.com/gcm/send'
    data = {'to':'/topics/global', 'data' : {'msg':cloudMsg} }
    responseData = ''
    try:
        for API_KEY in API_KEYS:
            print API_KEY, cloudMsg
            headers  =  {'Content-Type' : 'application/json', 'Authorization' : 'key='+API_KEY}
            request  =  urllib2.Request(url, json.dumps(data), headers)
            response = urllib2.urlopen(request)
            responseData = response.read()
            print "send >>> key=%s >>> value=%s >>> result=%s" %(API_KEY, cloudMsg, responseData)
    except Exception, e:
        print format_exc()

def Main():
    socket.setdefaulttimeout(2.0)

    configFile = open("configs/main.json", "r")
    configs = json.loads(configFile.read())
    configFile.close()

    redisConfig = configs["Redis"]
    print "Connecting to redis...",
    redisDB = redis.Redis(
        redisConfig["Hostname"],
        redisConfig["Hostport"],
        redisConfig["Database"],
        redisConfig["Password"]
    )
    print "ok"

    while True :
        curTime = int(time.time())
        time.sleep(1)

        if curTime % 10 == 0:
            print "[%s, totalmsg:%s] "%(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(curTime)), redisDB.llen("goolecloudmsg"))
        try:
            if curTime % 60 == 0:
                if redisDB.llen("goolecloudmsg") != 0:
                    msgData = redisDB.blpop("goolecloudmsg")[1]
                    infos = msgData.split("|")
                    sendTime = int(time.time())
                    if len(infos[0]) !=0 and infos[0] != "":
                        sendTime = time.mktime(time.strptime(infos[0],'%Y-%m-%d %H:%M'))
                    if time.time() > sendTime:
                        sendGCM(infos[1])
                    else:
                        redisDB.rpush("goolecloudmsg", msgData)

        except:
            print_exc()

if __name__ == "__main__":
    Main()

