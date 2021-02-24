from datetime import datetime, timedelta


class JoachimDb:
    def __init__(self, db, config):
        self.config = config
        self.conn = db
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS joachim (type varchar(3), date timestamp)"
        )

    def alert(self, alert_type):
        now = datetime.now()
        last = self.conn.execute(
            "SELECT date FROM joachim WHERE TYPE = ? ORDER BY date DESC LIMIT 1",
            (alert_type,),
        ).fetchone()

        if last is None or now - last[0] < timedelta(seconds=self.config.joachim_timeout):
            print("Spam detected")
            return

        self.conn.execute("INSERT INTO joachim VALUES (?,?)", (alert_type, now))
        self.conn.commit()

    def overview(self, alert_type):
        now = datetime.now()
        sql = "SELECT count(*) FROM joachim WHERE date > ? AND type = ?"

        return (
            (self.conn.execute(sql, [now - timedelta(minutes=timestamp), alert_type]).fetchone()[0]) for timestamp in
            self.config.joachim_timestamps
        )
