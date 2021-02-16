import discord as dc 
from dotenv import load_dotenv
from os import getenv
import datetime as dt
import json
load_dotenv()

#*#*#*# variables #*#*#*#
config_relative_path = getenv("CONFIG")
database_relative_path = getenv("DATABASE")
token = getenv("TOKEN")
#*#*#*#*#*#*#*#*#*#*#*#*#


with open(config_relative_path) as f:
    cfg = json.load(f)
with open(database_relative_path) as f:
    db = json.load(f)


class BOT(dc.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prefix = cfg['prefix']
        self.perms = cfg['perms']

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
                if delRan in range(1,51):
                    await message.channel.purge(limit=delRan+1, bulk=True)
                else:
                    await message.reply("Purge amount must be in range from `1` to `50`.")

        # user info embed getter
        elif content.startswith("me") and await self.checkPerms(message, "me"):
            if len(message.mentions) == 1:
                await self.getMeEmbed(message, message.mentions[0])
            else:
                await self.getMeEmbed(message)

        # role/channel ID getter, may add chaining id's, unnecessary for now
        elif command == "id" and await self.checkPerms(message, "id"):
            if args[0] != None:
                if len(message.role_mentions) == 1:
                    await message.channel.send(f"id: `{message.role_mentions[0].id}`")
                elif len(message.channel_mentions) == 1:
                    await message.channel.send(f"id: `{message.channel_mentions[0].id}`")
                elif len(message.mentions) == 1:
                    await message.channel.send(f"id: `{message.mentions[0].id}`")
            else:
                await message.channel.send(f'syntax: `{self.prefix}id role / channel / mention`, returns id')

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
                    if lvl not in range(1,3):
                        await message.reply("Perms level can only be 1 or 2")
                    else:
                        if self.managePerms("set", level=lvl, role=role_id):
                            await message.reply("Role permission changed successfully")
                        else:
                            await message.reply("Error occured while changing role permissions.")

            elif (args[0] == "delete" or args[0] == "del") and await self.checkPerms(message, "permissions_manage"):
                if len(args) == 2:
                    if len(message.role_mentions) == 1:
                        role_id = message.raw_role_mentions[0]
                    else:
                        role_id = args[1]
                    if self.managePerms("delete", role=role_id):
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

        # change log channel
        elif command == "log" and await self.checkPerms(message, "log"):
            if args[0] == "change" and len(args) == 2:
                await message.reply(await self.changeLogChannel(message=message, channel=args[1]))
            else:
                await message.reply(f"Something is wrong - chnl = {args[1]}")

        # new semester
        elif command == "newSemester" and await self.checkPerms(message, "newSemester"):
            await message.reply(f"Are you sure? `{self.prefix}Yes` or `{self.prefix}No`")
            newSemFlag = True

        elif command == "Yes" and await self.checkPerms(message, "newSemester"):
            if newSemFlag == True:
                newSemester(self, message)
                newSemFlag == False
                print("New sem has begun")

        elif command == "No":
            newSemFlag = False

        # log changes
        await BOT.logCommand(self, message, command)

    # KONIEC ON_COMMAND ***********************************************************************************************

    def getUserPerms(self, user):
        lvls = [0]
        for pLvl, pRoles in db['permRoles'].items():
            if any([role.id in pRoles for role in user.roles]):
                lvls.append(int(pLvl))
        permLevel = max(lvls)
        return permLevel

    async def checkPerms(self, message, command):
        try:
            required = cfg["perms"][command]
        except:
            required = float('infinity')
        if self.getUserPerms(message.author) >= required:
            return True
        else:
            await message.reply("You don't have the permission to use this command.")
            return False

    def getAvatarURL(self, user):
        base = "https://cdn.discordapp.com/avatars/"
        return base + str(user.id) + "/" + str(user.avatar)

    async def getMeEmbed(self, message, user = None):
        embed = dc.Embed(title="User info")
        if not user:
            user = message.author
        embed.color = user.color
        embed.set_image(url=self.getAvatarURL(user))

        joined_info = f"Joined server on `{user.joined_at.strftime('%d/%m/%Y')}`"
        joined_info += f"\nBeen here for: `{str(dt.datetime.now() - user.joined_at).split(',')[0]}`"

        print(user.roles)
        user_roles = [role.mention for role in user.roles if role.name != "@everyone"]
        if not any(user_roles):
            roles_info = "No roles to see here!"
        else:
            roles_info = ", ".join(user_roles)

        # ranking_info =

        embed.add_field(name="Join Date", value=joined_info, inline=False)
        embed.add_field(name="User Roles", value=roles_info, inline=False)
        # embed.add_field(name="Ranking", value=ranking_info, inline=False)
        await message.channel.send(embed=embed)

    def saveDatabase(self):
        with open(database_relative_path, mode="w") as f:
            json.dump(db, f, indent=4)

    def setPrefix(self, new_prefix):
        cfg["prefix"] = new_prefix
        with open(config_relative_path, mode="w") as f:
            json.dump(cfg, f, indent=4)
        self.prefix = new_prefix

    def getLeaderboard(self, guild, lenght = 5):
        ranking = db["ranking"]
        ranking.sort(key = lambda x: x["exp"], reverse = True)
        lb = ""
        r=1
        for i in range(min(len(ranking), lenght, 15)):
            user = ranking[i]
            if not guild.get_member(user['id']):
                lb+=f"#{r} {guild.get_member(user['id'])}: {user.get('exp')}\n"
                r+=1
        print(lb)
        return lb

    def managePerms(self, command, **args):
        if command == "set":
            try:
                level = args["level"]
                role = args["role"]
            except:
                return False
            else:
                for pLvl, pRoles in db["permRoles"].items():
                    if role in pRoles:
                        if int(pLvl) == level:
                            return True
                        db["permRoles"][pLvl] = [r for r in db["permRoles"][pLvl] if r != role]
                        break
                db["permRoles"][str(level)].append(role)
                self.saveDatabase()
                return True
        elif command == "delete":
            try:
                role = args["role"]
            except:
                return False
            else:
                for pLvl, pRoles in db["permRoles"].items():
                    if role in pRoles:
                        db["permRoles"][pLvl] = [r for r in db["permRoles"][pLvl] if r != role]
                        self.saveDatabase()
                        return True
                return False

    async def logCommand(self, message, command):

        # `Ktoś` użył `komenda` na `tam`

        log_value = cfg['log_channel_id']  # zainicjować przy starcie bota
        log_channel = BOT.get_channel(self=self, id=log_value)
        await log_channel.send(f"{message.author.mention} użył `{command}` na {message.channel.mention}")

    async def changeLogChannel(self, message, channel):
        guild_var = BOT.get_guild(self, id=cfg["guild_id"])
        for x in guild_var.channels:
            if x.name == channel:
                channel_obj = x
                break
        cfg["log_channel_id"] = channel_obj.id
        with open(config_relative_path, mode="w") as f:
            json.dump(cfg, f, indent=4)
        result_string = f'Log channel changed to {channel}'
        return result_string

    def newSemester(self, message):
        # https://discordpy.readthedocs.io/en/latest/api.html#discord.TextChannel.edit
        # a no tentego i trzeba dodać więcej opcji (argumentó)
        # Trzeba najpierw przenosić kanały, dopiero usuwać kategorie
        # if czy jest już kanał o tej nazwie
        newSemName = "OldSem"
        await dc.Guild.create_category(name=newSemName, position=-1) # ciekawe czy zadziała -1
        # domyślnie dc tworzy kategorię na samym dole, może nie trzeba -1
        tmp = 0
        list_channels = dc.Guild.channels
        channel_amount = len(list_channels)
        while tmp <= list_channels: # nie jestem pewny czy <= czy <
            # tmp = list index
            await list_channels[tmp].edit(sync_permissions=True, position=channel_amount+1)
            channel_amount+=1
            tmp+=1
        # dobra czyli wszystkie kanały przeniesione na sam dół w takiej kolejnośći jak były
        # trzeba ew jakieś wyjątki zrobić jak na przykład przy kanale powitalnym, głosowych itd
        # omatko trzeba jeszcze pododawać role, dodać rolę archiwum

#         zmiana kanału do logów





bot_client = BOT()
bot_client.run(token)