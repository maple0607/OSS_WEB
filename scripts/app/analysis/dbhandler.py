import MySQLdb
from app.utils.views import *

class DBHandler:
    def __init__(self, name, serverId, sqltype, user, password, host, port, dbname, charset="utf8"):
        self.mName = name
        self.mServerID = serverId
        self.mType = sqltype.lower()
        self.mConnParams = [user, password, host, port, dbname, charset]
        self.mConnection = None
        self.mCursor = None

    def getHandlerInfo(self):
        return [param for param in self.mConnParams]

    def setUser(self, user):
        self.mConnParams[0] = user

    def setPassword(self, passwd):
        self.mConnParams[1] = passwd

    def setHost(self, host):
        self.mConnParams[2] = host

    def setPort(self, port):
        self.mConnParams[3] = port

    def setDBName(self, dbname):
        self.mConnParams[4] = dbname

    def getName(self):
        return self.mName

    def getType(self):
        return self.mType

    def getServerID(self):
        return self.mServerID

    def begin(self):
        if self.mConnection == None and self.mCursor == None:
            try:
                self.mConnection = MySQLdb.connect(
                    user    = self.mConnParams[0],
                    passwd  = self.mConnParams[1],
                    host    = self.mConnParams[2],
                    port    = self.mConnParams[3],
                    db      = self.mConnParams[4],
                    charset = self.mConnParams[5])
                self.mCursor = self.mConnection.cursor()
                return True
            except:
                self.end()
                cv.err("Connected to MySQL failed!", True)
        else:
            cv.err("Handler has already connected!", True)
        return False

    def end(self):
        if self.mCursor:
            self.mCursor.close()
            self.mCursor = None
        if self.mConnection:
            self.mConnection.close()
            self.mConnection = None

    def executeSql(self, sqlString):
        results = []
        if self.begin():
            try:
                self.mCursor.execute(sqlString)
                results = self.mCursor.fetchall()
            except:
                cv.warn("Query failed! SQL:" + sqlString, True)
                results = ()
        self.end()
        return results