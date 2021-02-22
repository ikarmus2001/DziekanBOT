from .joachim_utils.db import JoachimDb
from .joachim_utils.joachin_messages import JoachimMessages


class Joachim:
    def __init__(self):
        self.db = JoachimDb()
        self.mes = JoachimMessages()

    async def overview(self, message_obj, args):
        if "pdp" in args:
            val = self.db.overview("pdp")
            mess_type = "pdp"
        elif "rasberry" in args:
            val = self.db.overview("ras")
            mess_type = "ras"
        elif "japonce" in args:
            val = self.db.overview("jap")
            mess_type = "jap"

        await message_obj.reply(self.mess.overview_message(mess_type, val))

    async def alert(self,message,args):
        if "pdp" in args:
            self.db.alert("pdp")
            await message.reply(self.mess.pdp_message())

        elif "rasberry" in args:
            self.db.alert("ras")
            await message.reply(self.mess.rasberry_message())

        elif "japonce" in args:
            self.db.alert("jap")
            await message.reply(self.mess.jap_message())

# Jochaim alerts
# To do
# sprawdzic czy aktualnie odbywaja sie zajecia
# zrobic ładny wykres ?
# dodac system losowania wiadomosci podczas alertow

