from commands.joachim.db import JoachimDb
from commands.joachim.joachin_messages import JoachimMessages


class Joachim:
    def __init__(self, db_conn, config):
        self.db = JoachimDb(db_conn,config)
        self.mess = JoachimMessages(db_conn, config)

    async def overview(self, message_obj, args):
        if "pdp" in args:
            val = self.db.overview("pdp")
            mess_type = "pdp"
        elif "raspberry" in args:
            val = self.db.overview("ras")
            mess_type = "ras"
        elif "japonce" in args:
            val = self.db.overview("jap")
            mess_type = "jap"

        await message_obj.reply(self.mess.overview_message(mess_type, val))

    async def alert(self, message, args):
        if "pdp" in args:
            self.db.alert("pdp")
            await message.reply(self.mess.pdp_message())

        elif "raspberry" in args:
            self.db.alert("ras")
            await message.reply(self.mess.raspberry_message())

        elif "japan" in args:
            self.db.alert("jap")
            await message.reply(self.mess.jap_message())


# Jochaim alerts
# To do
# sprawdzic czy aktualnie odbywaja sie zajecia
# zrobic ładny wykres ?
# dodac system losowania wiadomosci podczas alertow
