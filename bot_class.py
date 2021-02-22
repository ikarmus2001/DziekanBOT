import commands
import discord as dc
import datetime as dt

# from dotenv import load_dotenv
# from os import getenv
# import json
#
# load_dotenv()
#
# # *#*#*# variables #*#*#*#
# config_relative_path = getenv("CONFIG")
# database_relative_path = getenv("DATABASE")
# token = getenv("TOKEN")
# # *#*#*#*#*#*#*#*#*#*#*#*#
#
#
# with open(config_relative_path) as f1:
#     cfg = json.load(f1)
#
# with open(database_relative_path) as f2:
#     db = json.load(f2)

db, cfg, token = commands.loadingAssets()


class BOT(dc.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prefix = cfg['prefix']
        self.perms = cfg['perms']
        # self.cmd = cmd
        # self.db = db

    async def on_ready(self):
        for guild in self.guilds:
            print(f"{self.user} connected to {guild.name}, id: {guild.id}")
        print(f"{self.user.name} is alive!")

    async def on_message(self, message):
        if message.author == self.user:
            return
        if message.content.startswith(self.prefix):
            await self.command(message)
        elif (self.user.name + " ssie") in message.content or (self.user.name + " sucks") in message.content:
            await message.reply("૮( ᵒ̌▱๋ᵒ̌ )ა ?!")

    async def command(self, message):
        content = message.content[len(self.prefix):]
        args = content.split()[1::] if len(content.split()) > 1 else [None]
        command = content.split()[0]

        if content == "hi":
            await message.reply("hi!")

        # user info embed getter
        elif content.startswith("me"):
            if len(message.mentions) == 1:
                await self.getMeEmbed(message, message.mentions[0])
            else:
                await self.getMeEmbed(message)

        # role/channel ID getter
        elif command == "id":
            if len(args) == 1:
                if len(message.role_mentions) == 1:
                    await message.channel.send(f"id: `{message.role_mentions[0].id}`")
                elif len(message.channel_mentions) == 1:
                    await message.channel.send(f"id: `{message.channel_mentions[0].id}`")
                elif len(message.mentions) == 1:
                    await message.channel.send(f"id: `{message.mentions[0].id}`")

        # avatar getter
        elif command == "avatar" or command == "av":
            if message.mentions:
                avatar_url = self.getAvatarURL(message.mentions[0])
            else:
                avatar_url = self.getAvatarURL(message.author)
            await message.reply(avatar_url)

        # perms getter/setter
        elif command == "perms" or command == "permissions":
            if args[0] == "add":
                if self.checkPerms(message.author, 2):
                    try:
                        lvl = args[1]
                        role_id = message.channel_mentions[0]
                    except:
                        await message.reply(
                            f"{message.author.mention} please specify a permission level and role to assign the permission to.")
                else:
                    await message.reply("Your permission level is too low to use this command!")
            else:
                perm_lvl = self.getUserPerms(message.author)
                await message.reply(f"Your permission level: `{perm_lvl}`")

        # bot prefix setter
        elif command == "prefix":
            if args[0]:
                self.setPrefix(args[0])
                await message.channel.send(f"Prefix successfully set to: `{args[0]}`")

        # leaderboard getter
        elif command == "leaderboard":
            lb_len = 5
            if args[0]:
                try:
                    lb_len = int(args[0])
                except:
                    await message.reply(f"Please specify the leaderboard lenght like: `{self.prefix}leaderboard 10`")
            lb = self.getLeaderboard(message.guild, lb_len)
            await message.channel.send(lb)

    async def getMeEmbed(self, message, user=None):
        embed = dc.Embed(title="User info")
        if not user:
            user = message.author
        embed.color = user.color
        embed.set_image(url=self.getAvatarURL(user))

        joined_info = f"Joined server on `{user.joined_at.strftime('%d/%m/%Y')}`"
        joined_info += f"\nBeen here for: `{str(dt.datetime.now() - user.joined_at).split(',')[0]}`"

        user_roles = [role.name for role in user.roles if role.name != "@everyone"].reverse()
        if not user_roles:
            roles_info = "No roles to see here!"
        else:
            roles_info = ", ".join(user_roles)

        # ranking_info =

        embed.add_field(name="Join Date", value=joined_info, inline=False)
        embed.add_field(name="User Roles", value=roles_info, inline=False)
        # embed.add_field(name="Ranking", value=ranking_info, inline=False)
        await message.channel.send(embed=embed)
