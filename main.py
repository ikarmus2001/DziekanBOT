import discord as dc
from dotenv import load_dotenv
from os import getenv
import json

load_dotenv()
token = getenv("DISCORD_TOKEN")

with open(r'config.json') as f:
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

        if content.startswith("avatar") or content.startswith("av"):
            avatar_url = self.getAvatarURL(message.author)
            await message.send(message.reply(avatar_url))

        elif content.startswith("me"):
            # embd =
            await self.me_richtext(message, message.author)  # message.author

    def getAvatarURL(self, user):
        base = "https://cdn.discordapp.com/avatars/"
        return base + str(user.id) + "/" + str(user.avatar)

    async def me_richtext(self, message, user, title="Title", color=0x00ff00, desc="Short description"):
        embd = dc.Embed(title=title, description=desc, color=color)
        embd.set_image(url=self.getAvatarURL(user))
        joinDate = user.created_at.strftime("%d, %Y")  # when user created profile
        embd.add_field(name="Dołączenie", value="Jesteś z nami już od {}".format(joinDate), inline=True)
        embd.add_field(name="Field2", value="hi2", inline=True)
        await message.channel.send(embed=embd)


bot_client = BOT()
bot_client.run(token)
