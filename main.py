import discord as dc
from dotenv import load_dotenv
from os import getenv
import json
import datetime

load_dotenv()
token = getenv("DISCORD_TOKEN")

with open(r'config.json') as f:
    cfg = json.load(f)


class BOT(dc.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prefix = cfg['prefix']
        # print(type(cfg))

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

        elif content.startswith("avatar") or content.startswith("av"):
            avatar_url = self.getAvatarURL(message.author)
            await message.channel.send(message.reply(avatar_url))

        elif content.startswith("me"):
            await self.me_richtext(message, message.author)

        elif content.startswith("prefix"):
            content_func = content[7:]  # uwzględniam spację
            print(content_func)
            if content_func.startswith("change"):
                new_prefix = content_func.split(" ")[-1]
                await message.channel.send("Zmieniasz prefix na {}".format(new_prefix))
                print(new_prefix)
                await message.channel.send(await bot_client.prefix_change(new_prefix=new_prefix))
            else:
                await message.channel.send("Aktualny prefix: {}".format(cfg["prefix"]))

    def getAvatarURL(self, user):
        base = "https://cdn.discordapp.com/avatars/"
        return base + str(user.id) + "/" + str(user.avatar)

    async def me_richtext(self, message, user, title="Title", color=0xff0000, desc=None):
        embd = dc.Embed(title=title)
        embd.set_image(url=self.getAvatarURL(user))

        if desc:
            embd.description(desc)

        join_date_date = user.joined_at
        join_date_string = join_date_date.strftime("%Y, %m, %d")  # when user created profile
        day_amount = str(datetime.datetime.now() - join_date_date)
        join_value = "Jesteś z nami już od {}, \nco daje w sumie {}!".format(join_date_string, day_amount)

        roles = []
        for x in user.roles:
            if x.name != '@everyone':
                roles.append(x.mention)
        if len(roles) == 0:
            roles = "Nikt Cię nie wtajemniczył?"  # Napisz do {}!".format(dc.Role.mention) wyciąganie z bazy
        else:
            roles.reverse()
            color = user.color
            roles = ", ".join(roles)
        embd.color = color

        embd.add_field(name="Dołączenie", value=join_value, inline=False)
        embd.add_field(name="Twoje role:", value=roles, inline=False)
        # embd.add_field(name=)
        await message.channel.send(embed=embd)

    async def prefix_change(self, new_prefix):
        print("Changing prefix - entering method")
        cfg["prefix"] = new_prefix
        self.prefix = new_prefix
        f = open("config.json", "w")
        json.dump(cfg, f)
        f.close()
        result = "Prefix changed to {}, exiting method".format(new_prefix)  # by someone
        print(result)
        return result


bot_client = BOT()
bot_client.run(token)
