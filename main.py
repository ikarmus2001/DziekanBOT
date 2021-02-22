import commands
from dotenv import load_dotenv
from os import getenv
import json


load_dotenv()

# *#*#*# variables #*#*#*#
config_relative_path = getenv("CONFIG")
database_relative_path = getenv("DATABASE")
joachim_relative_path = getenv("JOACHIM")
token = getenv("TOKEN")
# *#*#*#*#*#*#*#*#*#*#*#*#


with open(config_relative_path) as f:
    cfg = json.load(f)
with open(database_relative_path) as f:
    db = json.load(f)
with open(joachim_relative_path) as f:
    joachim = json.load(f)


class BOT(commands.Commands):
    def __init__(self, intents=None, *args, **kwargs):
        super().__init__(*args, **kwargs, intents=intents)
        self.prefix = cfg['prefix']
        self.perms = cfg['perms']
        self.debugging = db['debugMode']
        self.joachim = joachim['joachim']

    async def on_ready(self):
        await self.loadLogsChannel()
        for guild in self.guilds:
            print(f"{self.user} connected to {guild.name}, id: {guild.id}")
        print(f"{self.user.name} is alive!")

    async def on_message(self, message):
        if message.author == self.user:
            return
        elif db["groupReg"]["active"] and message.channel.id == db["groupReg"]["channel_id"]:
            if "lab" in message.content.lower() or "mat" in message.content.lower():
                await self.groupReg(message)
        elif message.content.startswith(self.prefix):
            await self.command(message)
        elif (self.user.name + " ssie") in message.content or (self.user.name + " sucks") in message.content:
            await message.reply("૮( ᵒ̌▱๋ᵒ̌ )ა ?!")

    async def command(self, message):
        content = message.content[len(self.prefix):]
        args = content.split()[1::] if len(content.split()) > 1 else [None]
        command = content.split()[0]

        # say command 
        if command == "say" and await self.checkPerms(message, "say"):
            await message.delete()
            if any(args):
                await message.channel.send(" ".join([arg for arg in args]))

        # message purge 
        elif command == "purge" and await self.checkPerms(message, "purge"):
            try:
                delRan = int(args[0])
            except:
                await message.reply("Please specify how many messages to purge.")
            else:
                if delRan in range(1, 51):
                    await message.channel.purge(limit=delRan + 1, bulk=True)
                    if self.logsActive: await self.log(message)
                else:
                    await message.reply("Purge amount must be in range from `1` to `50`.")

        # user info embed getter
        elif command == "me" and await self.checkPerms(message, "me"):
            if len(message.mentions) == 1:
                await message.channel.send(embed=self.getMeEmbed(message, message.mentions[0]))
            else:
                await message.channel.send(embed=self.getMeEmbed(message))

        # role/channel ID getter
        elif command == "id" and await self.checkPerms(message, "id"):
            if len(args) == 1:
                if len(message.role_mentions) == 1:
                    await message.channel.send(f"id: `{message.role_mentions[0].id}`")
                elif len(message.channel_mentions) == 1:
                    await message.channel.send(f"id: `{message.channel_mentions[0].id}`")
                elif len(message.mentions) == 1:
                    await message.channel.send(f"id: `{message.mentions[0].id}`")

        # avatar getter
        elif command == "avatar" or command == "av" and await self.checkPerms(message, "avatar"):
            if message.mentions:
                avatar_url = self.getAvatarURL(message.mentions[0])
            else:
                avatar_url = self.getAvatarURL(message.author)
            await message.reply(avatar_url)

        # perms getter/setter
        elif command == "perms" or command == "permissions" and await self.checkPerms(message, "permissions"):
            if args[0] == "set" and len(args) == 3 and await self.checkPerms(message, "permissions_manage"):
                try:
                    lvl = int(args[2])
                    if len(message.role_mentions) == 1:
                        role_id = message.raw_role_mentions[0]
                    else:
                        role_id = args[1]
                except:
                    await message.reply(f"Please specify a permission level and role to assign the permission to.")
                else:
                    if lvl not in range(1, 3):
                        await message.reply("Perms level can only be 1 or 2")
                    else:
                        if self.managePerms("set", level=lvl, role=role_id):
                            await message.reply("Role permission changed successfully")
                            if self.logsActive:
                                await self.log(message)
                        else:
                            await message.reply("Error occurred while changing role permissions.")

            elif (args[0] == "delete" or args[0] == "del") and await self.checkPerms(message, "permissions_manage"):
                if len(args) == 2:
                    if len(message.role_mentions) == 1:
                        role_id = message.raw_role_mentions[0]
                    else:
                        role_id = args[1]
                    if self.managePerms("delete", role=role_id):
                        if self.logsActive: await self.log(message)
                        await message.reply("Role permission deleted successfully")
                    else:
                        await message.reply("Error occured while deleting role permissions.")
                else:
                    await message.reply(f"Please specify a role to delete the permission from.")

            elif not any(args):
                perm_lvl = self.getUserPerms(message.author)
                await message.reply(f"Your permission level: `{perm_lvl if perm_lvl < 3 else 'GOD'}`")

        # bot prefix setter
        elif command == "prefix" and await self.checkPerms(message, "prefix"):
            if args[0]:
                self.setPrefix(args[0])
                await message.channel.send(f"Prefix successfully set to: `{args[0]}`")
                if self.logsActive: await self.log(message)

        # leaderboard getter
        elif command == "leaderboard" and await self.checkPerms(message, "leaderboard"):
            lb_len = 5
            if args[0]:
                try:
                    lb_len = int(args[0])
                except:
                    await message.reply(f"Please specify the leaderboard lenght like: `{self.prefix}leaderboard 10`")
            lb = self.getLeaderboard(message.guild, lb_len)
            await message.channel.send(lb)

        # debug mode 
        elif (command == "debug" or command == "debugging") and await self.checkPerms(message, "debugging"):
            if args[0] == "on" or args[0] == "true" or args[0] == "1":
                if self.debugging:
                    await message.reply("Debugging mode is already `on`")
                else:
                    self.debugging = db['debugMode'] = True
                    self.saveDatabase()
                    if self.logsActive:
                        await self.log(message)
                    await message.reply("Debugging mode has been successfully turned `on`")

            elif args[0] == "off" or args[0] == "false" or args[0] == "0":
                if not self.debugging:
                    await message.reply("Debugging mode is already `off`")
                else:
                    self.debugging = db['debugMode'] = False
                    self.saveDatabase()
                    if self.logsActive: await self.log(message)
                    await message.reply("Debugging mode has been successfully turned `off`")

        # logs management
        elif command == "logs" and await self.checkPerms(message, "logs"):
            if args[0] == "set":
                if len(args) == 2 and len(message.channel_mentions) == 1:
                    await self.setLogsChannel(message.channel_mentions[0].id)
                    await message.reply(f"Logs channel successfully set to {message.channel_mentions[0].mention}")
                else:
                    await message.reply(f"Please specify a log channel like: `{self.prefix}logs set #someLogsChannel`")
            elif len(args) == 1 and (args[0] == "on" or args[0] == "true" or args[0] == "1"):
                self.logsActive = True
                db['logs']['active'] = True
                self.saveDatabase()
                if self.logsActive: await self.log(message)
                await message.reply("Logs are now turned `on`")
            elif len(args) == 1 and (args[0] == "off" or args[0] == "false" or args[0] == "0"):
                if self.logsActive: await self.log(message)
                self.logsActive = False
                db['logs']['active'] = False
                self.saveDatabase()
                await message.reply("Logs are now turned `off`")

        # semester management
        elif (command == "semester" or command == "sem") and await self.checkPerms(message, "semester_manage"):
            if args[0] == "new" or args[0] == "start":
                if not db["groupReg"]["active"]:
                    try:
                        group_count = int(args[1])
                    except:
                        await message.reply(f"Please specify the number of groups like: `{self.prefix}semester new 8`")
                    else:
                        if await self.openGroupReg(message, group_count):
                            await message.reply("New semester started successfully!")
                            if self.logsActive:
                                await self.log(message)
                        else:
                            await message.reply("An error has occured while creating new semester.")
                else:
                    await message.reply("Group registration is already open!")
            elif args[0] == "close" or args[0] == "end":
                if db["groupReg"]["active"]:
                    await self.closeGroupReg(message)
                    if self.logsActive: await self.log(message)
                    await message.reply("Group registration has successfully been closed.")
                else:
                    await message.reply("There's no group registration currently ongoing to close!")

    # *=*=*=*=*=*=*=*=* COMMANDS *=*=*=*=*=*=*=*=* #


intents = dc.Intents.all()
bot_client = BOT(intents=intents)
bot_client.run(token)
