""" Simple database for a Telegram bot """
import sqlite3
import datetime

class Database(object):
    """ Class representing a database """
    def __init__(self, filename):
        self.conn = sqlite3.connect(filename)
        self.c = self.conn.cursor()
        if self.c.execute("SELECT name FROM sqlite_master WHERE \
            type='table' AND name='HISTORY';").fetchone() is None:
            self.conn.execute('''CREATE TABLE HISTORY
                (TIME  INT      NOT NULL,
                LIGHTS  BOOLEN NOT NULL,
            PROJECTOR   BOOLEAN);''')
            print "new table created"

    def addData(self, time, lights, projector):
        """ Add a data point to the database """
        if lights:
            lights = 1
        self.conn.execute("INSERT INTO HISTORY (TIME,LIGHTS,PROJECTOR) \
        VALUES (?, ?, ?)", [time, lights, projector])
        self.conn.commit()

    def printDB(self):
        """ Print the database content """
        print "DB:"
        self.c.execute('SELECT * FROM history ORDER BY time')
        for row in self.c:
            print row

    def lastLights(self):
        """ Returns the last time when lights were on """
        self.c.execute('SELECT time FROM history WHERE lights = 1 ORDER BY time DESC LIMIT 1')
        result = self.c.fetchone()
        if result is None:
            return "ei koskaan"
        else: result = result[0]
        return datetime.datetime.fromtimestamp(
            int(result)).strftime('%H:%M:%S %Y/%m/%d')
