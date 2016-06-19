import MySQLdb
import MySQLdb.cursors 

class Db():

    def __init__(self, host, user, passwd, dbname, port=3306):
        self._db = MySQLdb.connect(host=host, port=port, user=user, passwd=passwd, db=dbname, cursorclass=MySQLdb.cursors.DictCursor)

    def run_query(self, sql):
        try:
            c = self._db.cursor()
            c.execute(sql)
            data = c.fetchall()
            return data
        except Exception as e:
            print(e)
            return None
