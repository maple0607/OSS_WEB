#coding=utf8

from app.utils.tabfile import TabFile

LevelRankRewards = [
    [[[5,55080001,100], [4,44330001,100], [4,44310002,100], [2,2000]], "desc"],
    [[[5,55080001,100], [4,44330001,100], [4,44310002,100], [2,2000]], "desc"],
]

PowerRankRewards = [

]


def LoadCfgs():
    global LevelRankRewards
    global PowerRankRewards
    LevelRankRewards = LoadCfg("configs/rewards/levelRankrewards.txt")
    PowerRankRewards = LoadCfg("configs/rewards/powerRankreward.txt")
    #print(LevelRankRewards)
    #print(PowerRankRewards)

def LoadCfg(filename):
    cfg = []
    tb = TabFile()
    if tb.load(filename):
        for i in xrange(tb.mRowNum):
            strAwards = tb.get(i, 2, "", False)
            strContents = tb.get(i, 3, "", False)
            aaa = []
            awards = []
            strAward = strAwards.split(';')
            for str in strAward:
                if str != "":
                    strList = str.split(",")

                    strList_n = []
                    for strN in strList:
                        strList_n.append(int(strN))

                    awards.append(strList_n)
            aaa.append(awards)
            aaa.append(strContents)
            cfg.append(aaa)

    return cfg

LoadCfgs()

