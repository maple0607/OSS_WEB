#coding=utf8

import os
import re
import sys

def isChineseWord(uchar):
    return 0x4e00<=ord(uchar)<0x9fa6

def hasChineseWord(tmpString):
    for i in tmpString:
        if isChineseWord(i):
            return True
    return False

filedata = {}

targetStringFilename = "strings.nws.txt"

if os.path.exists(targetStringFilename):
    tmpFile = open(targetStringFilename, "r")
    lines = tmpFile.readlines()
    tmpFile.close()
    for line in lines:
        tmpLine = "%s"% (line.replace("\n", "").replace("\r", ""))
        datas = tmpLine.split("\t")
        if len(datas) == 2:
            filedata[datas[0].decode("utf8")] = datas[1]

for root, dirs, files, in os.walk("templates"):
    for f in files:
        filename = root + "/" + f
        targetFilename = os.path.abspath(filename)
        print targetFilename
        if filename.endswith(".html"):
            tmpFile = open(filename, "r")
            data = tmpFile.read()
            tmpFile.close()
            needSave = False
            data = data.decode("utf8")
            dataList = re.findall(ur"[\u4e00-\u9fa5]+", data)
            for d in dataList:
                if hasChineseWord(d):
                    needSave = True
                    if d in filedata and len(filedata[d]) != 0:
                        data = data.replace(d, filedata[d])
            if needSave:
                tmpDir = os.path.split(targetFilename)[0]
                if not os.path.exists(tmpDir):
                    os.makedirs(tmpDir)
                tmpFile = open(targetFilename, "w")
                tmpFile.write(data.encode("utf8"))
                tmpFile.close()

