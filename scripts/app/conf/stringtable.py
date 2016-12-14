#coding:utf-8
import sys

class StringTable:
    def __init__(self):
        self.mTable = {}
        self.mLanCategory = []
        self.mLanguage = 0

    def new(self):
        self.loadTable("configs/stringtable/system.txt")
        return self

    def loadTable(self, fn):
        try:
            fileHD = open(fn)
            lines = fileHD.readlines()
            fileHD.close()
            self.mLanCategory = lines[0].replace("\n", "").replace("\r", "").split("\t")
            for i in xrange(1, len(lines)):
                nouns = lines[i].replace("\n", "").replace("\r", "").split("\t")
                self.mTable[nouns[0]] = nouns
        except:
            print "StringTable loading failed!"
            sys.exit(-1)

    def ST(self, nativeStr):
        try:
            return self.mTable[nativeStr][self.mLanguage]
        except:
            print "[StringTable][ERROR] %s + %s" %(nativeStr, self.mLanguage)
            return nativeStr

    def setLanguage(self, cate):
        if cate >= 0 and cate < len(self.mLanCategory):
            self.mLanguage = cate

    def getLanguages(self):
        lanDict = {}
        for i in xrange(len(self.mLanCategory)):
            lanDict[i] = self.mLanCategory[i]
        return lanDict

g_StrTable = StringTable().new()

def ST(nativeStr):
    return g_StrTable.ST(nativeStr)

def setLanguage(self, cate):
    g_StrTable.setLanguage(cate)

def getLanguages():
    return g_StrTable.getLanguages()