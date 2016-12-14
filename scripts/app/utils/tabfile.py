#coding=utf8

from traceback import print_exc

class TabFile:
    def __init__(self):
        self.mHeader = {}
        self.mRows = []
        self.mColNum = 0
        self.mRowNum = 0
    
    def load(self, filename):
        try:
            f = open(filename, "r")
            lines = f.readlines()
            f.close()
            
            header = True
            for line in lines:
                while line[-1:] == "\r" or line[-1:] == "\n":
                    line = line[:-1]
                    
                if header:
                    s = line.split("\t")
                    self.mColNum = len(s)
                    counter = 0
                    for i in s:
                        self.mHeader[i] = counter
                        counter += 1
                    header = False
                else:
                    if line[0] != "^":
                        s = line.split("\t")
                        if len(s) > 0:
                            self.mRows.append(s)
            self.mRowNum = len(self.mRows)
            return True
        except:
            print_exc()
            return False
        
    def get(self, row, col, defaultValue, isInteger = False):
        if type(row) != type(0):
            return defaultValue
        
        if type(col) == type(""):
            col = self.mHeader.get(col, -1)
        elif type(col) != type(0):
            return defaultValue
        
        if row >= 0 and row < len(self.mRows):
            if col >= 0 and col < len(self.mRows[row]):
                value = self.mRows[row][col]
                if isInteger:
                    try:
                        value = int(value)
                        return value
                    except:
                        return defaultValue
                else:
                    return value

        return defaultValue
        
        