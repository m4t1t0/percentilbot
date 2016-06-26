import MySQLdb
import MySQLdb.cursors 

class Db():

    def __init__(self, host, user, passwd, dbname, dbboname, port=3306):
        self.host = host
        self.port = port
        self.user = user
        self.passwd = passwd
        self.dbname = dbname
        self.dbboname = dbboname

    def connect(self):
        self._db = MySQLdb.connect(host=self.host, port=self.port, user=self.user, 
            passwd=self.passwd, db=self.dbname, cursorclass=MySQLdb.cursors.DictCursor)

    def get_dbname(self):
        return self.dbname

    def get_dbboname(self):
        return self.dbboname

    def close(self):
        self._db.close()

    def run_query(self, sql):
        try:
            self.connect()
            c = self._db.cursor()
            c.execute(sql)
            data = c.fetchall()
            self.close()
            return data
        except Exception as e:
            self.close()
            return None
