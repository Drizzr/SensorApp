import sqlite3
from sqlite3 import Error
from datetime import datetime
from main import app

FILE = "database.db"

class DataBase:
    """
    used to connect, write to and read from a local sqlite3 database
    """
    def __init__(self):
        """
        try to connect to file and create cursor
        """
        self.conn = None
        try:
            self.conn = sqlite3.connect("app/" + FILE)
        except Error as e:
            print(e)

        self.cursor = self.conn.cursor()

    def close(self):
        """
        close the db connection
        :return: None
        """
        self.conn.close()


    def delete_expired_token(self):
        query = f"DELETE FROM expired_token WHERE expiration_date <= {datetime.utcnow().timestamp()}"
        self.cursor.execute(query)
        self.conn.commit()
    
    def createRole(self, role_name, access_description):
        query = f"INSERT INTO role(name, access_scope) VALUES ('{role_name}', '{access_description}')"
        self.cursor.execute(query)
        self.conn.commit()



role_db = DataBase()

for role_name, scope in app.config["ROLES"].items():
    role_db.createRole(role_name, scope)
        
role_db.close()

