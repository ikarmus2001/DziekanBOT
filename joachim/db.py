import sqlite3
from datetime import datetime, timedelta


class joachim_db:
    def __init__(self):
        self.conn = sqlite3.connect("joachin.db")
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS joachim (type varchar(3), date timestamp)"
        )

    def alert(self, alert_type):
        self.conn.execute(
            "INSERT INTO joachim VALUES (?,?)", (alert_type, datetime.now())
        )
        self.conn.commit()

    def overview(self, type):
        now = datetime.now()
        sql = "SELECT count(*) FROM joachim WHERE date > ? AND type = ?"

        return (
            self.conn.execute(sql, [now - timedelta(minutes=5), type]).fetchone()[0],
            self.conn.execute(sql, [now - timedelta(minutes=10), type]).fetchone()[0],
            self.conn.execute(sql, [now - timedelta(minutes=15), type]).fetchone()[0],
            self.conn.execute(sql, [now - timedelta(minutes=30), type]).fetchone()[0],
            self.conn.execute(sql, [now - timedelta(minutes=60), type]).fetchone()[0],
        )
