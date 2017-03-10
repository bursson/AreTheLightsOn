""" Simple database for a Telegram bot """
import sqlite3
import datetime

class Database(object):
    """ Class representing a database. With type 0 uses sqlite3, with 1 simple variable"""
    def __init__(self, filename, dbtype=0):
        self.type = dbtype
        if self.type == 0:
            self.conn = sqlite3.connect(filename)
            self.c = self.conn.cursor()
            if self.c.execute("SELECT name FROM sqlite_master WHERE \
                type='table' AND name='HISTORY';").fetchone() is None:
                self.conn.execute('''CREATE TABLE HISTORY
                    (TIME  INT      NOT NULL,
                    LIGHTS  BOOLEN NOT NULL,
                PROJECTOR   BOOLEAN);''')
                print "new table created"
        elif self.type == 1:
            try:
                with open('backup.txt') as f:
                    self.lights = float(f.read().strip())
            except Exception as e:
                self.lights = 0
            self.projector = 0

    def addData(self, timestamp, lights, projector):
        """ Add a data point to the database """
        if self.type == 1:
            if lights:
                self.lights = timestamp
            if projector:
                self.projector = timestamp
            backup = open("backup.txt", 'w')
            backup.write(str(timestamp))
            backup.close()
        elif self.type == 0:
            if lights:
                lights = 1
            self.conn.execute("INSERT INTO HISTORY (TIME,LIGHTS,PROJECTOR) \
            VALUES (?, ?, ?)", [timestamp, lights, projector])
            self.conn.commit()

    def printDB(self):
        """ Print the database content """
        if self.type == 0:
            print "DB:"
            self.c.execute('SELECT * FROM history ORDER BY time')
            for row in self.c:
                print row
        elif self.type == 1:
            print "Lights: " + self.lights + ", projector: " + self.projector

    def lastLights(self):
        """ Returns the last time when lights were on """
        if self.type == 0:
            self.c.execute('SELECT time FROM history WHERE lights = 1 ORDER BY time DESC LIMIT 1')
            result = self.c.fetchone()
            if result is None:
                return "ei koskaan"
            else: result = result[0]
        else:
            result = self.lights
        return datetime.datetime.fromtimestamp(
            int(result)).strftime('%H:%M:%S %Y/%m/%d')
