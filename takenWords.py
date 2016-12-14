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

tmpDirDict = {}
tmpIndex = 0
tmpArray = []

targetStringFilename = "strings.nws.txt"

for root, dirs, files, in os.walk("templates"):
    for f in files:
        filename = root + "/" + f
        targetFilename = os.path.abspath(filename)
        print targetFilename
        if filename.endswith(".html"):
            tmpFile = open(filename, "r")
            data = tmpFile.read()
            tmpFile.close()
            data = data.decode("utf8")
            dataList = re.findall(ur"[\u4e00-\u9fa5]+", data)
            for d in dataList:
                curIdx = -1
                if d not in tmpDirDict:
                    curIdx = tmpIndex
                    tmpIndex += 1
                    tmpDirDict[d] = curIdx
                    tmpArray.append(d)
                else:
                    curIdx = tmpDirDict[d]

tmpFile = open(targetStringFilename, "w")
for i in tmpArray:
    tmpFile.write(i.encode("utf8").replace("\"", "") + "\n")
tmpFile.close()
os.system("pause")

