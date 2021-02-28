import sqlite3
from discord.ext.commands import Cog,command


class Notifier(Cog):
    def __init__(self):
        self.db = sqlite3.connect("notifications.db", detect_types=sqlite3.PARSE_DECLTYPES)
        self.db.execute(
            "CREATE TABLE IF NOT EXISTS notifications (channel_id varchar(50), subject varchar(10), text text)"
        )

