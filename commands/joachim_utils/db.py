import sqlite3
from datetime import datetime, timedelta


class JoachimDb:
    def __init__(self):
        self.conn = sqlite3.connect("joachin.db")
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS joachim_utils (type varchar(3), date timestamp)"
        )

    def alert(self, alert_type):
        now = datetime.now()
        self.conn.execute("SELECT DATE < ? FROM joachim_utils WHERE TYPE = ? LIMIT 1 ORDER BY date DESC").fetchone()[0]
        self.conn.execute("INSERT INTO joachim_utils VALUES (?,?)", (alert_type,now()))

    def overview(self, type):
        now = datetime.now()
        sql = "SELECT count(*) FROM joachim_utils WHERE date > ? AND type = ?"

        return (
            self.conn.execute(sql, [now - timedelta(minutes=5), type]).fetchone()[0],
            self.conn.execute(sql, [now - timedelta(minutes=10), type]).fetchone()[0],
            self.conn.execute(sql, [now - timedelta(minutes=15), type]).fetchone()[0],
            self.conn.execute(sql, [now - timedelta(minutes=30), type]).fetchone()[0],
            self.conn.execute(sql, [now - timedelta(minutes=60), type]).fetchone()[0],
        )