import MySQLdb
import MySQLdb.cursors 

class Db():

    def __init__(self, host, user, passwd, dbname, port=3306):
        self.host = host
        self.port = port
        self.user = user
        self.passwd = passwd
        self.dbname = dbname

    def connect(self):
        self._db = MySQLdb.connect(host=self.host, port=self.port, user=self.user, 
            passwd=self.passwd, db=self.dbname, cursorclass=MySQLdb.cursors.DictCursor)

    def close():
        self._db.MySQLdb.close()

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
