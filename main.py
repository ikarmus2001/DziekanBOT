import discord as dc 
from dotenv import load_dotenv
from os import getenv
import json

load_dotenv()
token = getenv("TOKEN")

with open(r'2021\q1\USIS_PythonBot\config.json') as f:
    cfg = json.load(f)

class BOT(dc.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prefix = cfg['prefix']

    async def on_ready(self):
        for guild in self.guilds:
            print(f"{self.user} connected to {guild.name}, id: {guild.id}")
        print(f"{self.user.name} is alive!")

    async def on_message(self, message):
        if message.author == self.user:
            return
        if message.content.startswith(self.prefix):
            await self.command(message)

    async def command(self, message):
        content = message.content[len(self.prefix):]
        if content == "hi":
            await message.reply("hi!")

        if content == "avatar" or content == "av":
            avatar_url = self.getAvatarURL(message.author)
            await message.reply(avatar_url)

    def getAvatarURL(self, user):
        base = "https://cdn.discordapp.com/avatars/"
        return base+str(user.id)+"/"+str(user.avatar)


bot_client = BOT()
bot_client.run(token)
