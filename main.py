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
        self.debugging = db['debugMode']
        self.newSemFlag = False

    async def on_ready(self):
        await self.loadLogsChannel()
        for guild in self.guilds:
            print(f"{self.user} connected to {guild.name}, id: {guild.id}")
        print(f"{self.user.name} is alive!")

    newSemFlag = False

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
                    if lvl not in range(1,3):
                        await message.reply("Perms level can only be 1 or 2")
                    else:
                        if self.managePerms("set", level=lvl, role=role_id):
                            await message.reply("Role permission changed successfully")
                            if self.logsActive: await self.log(message)
                        else:
                            await message.reply("Error occured while changing role permissions.")

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
                self.debugging = db['debugMode'] = True
                self.saveDatabase()
                if self.logsActive: await self.log(message)
                await message.reply("Debugging mode has been successfully turned `on`")
                
            elif args[0] == "off" or args[0] == "false" or args[0] == "0":
                self.debugging = db['debugMode'] = False
                self.saveDatabase()
                if self.logsActive: await self.log(message)
                await message.reply("Debugging mode has been successfully turned `off`")

        # logs manage
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

        # new semester
        elif command == "newSemester" and await self.checkPerms(message, "newSemester"):
            await message.reply(f"Are you sure? `{self.prefix}Yes` or `{self.prefix}No`")
            self.newSemFlag = True
            # https://discordpy.readthedocs.io/en/latest/api.html#discord.Client.wait_for
            # nie umiem tego napisać, wywala błąd z newSemFlag (odwołanie przed przypisaniem,
            # nawet gdy używam jej jako globalnej, a chyba w dodawanie flagi do DB się nie bawimy)
            # await dc.Client.wait_for(self, message, check=lambda: command == 'Yes') # <-- to nie działa

        elif command.capitalize() == "YES" or command.capitalize() == "Y": # and await self.checkPerms(message, "newSemester")
            print(self.newSemFlag)
            if self.newSemFlag == True: # <- to podobnie
                await self.newSemester(self, message=message)
                self.newSemFlag == False
                print("New sem has begun")
            else:
                print("newSemFlag = ", self.newSemFlag)
        elif command.capitalize() == "NO" or command.capitalize() == "N":
            self.newSemFlag = False

    # *=*=*=*=*=*=*=*=* COMMANDS *=*=*=*=*=*=*=*=* #

    def saveDatabase(self):
        with open(database_relative_path, mode="w") as f:
            json.dump(db, f, indent=4)

    async def loadLogsChannel(self):
        channel = await self.fetch_channel(db['logs']['id'])
        if channel: 
            self.logsChannel = channel
            self.logsActive = db['logs']['active']
        else:
            self.logsActive = db['logs']['active'] = False
            self.saveDatabase()
            print("Logs channel could not be found by id -- Logs were turned off.")

    async def setLogsChannel(self, channel_id):
        db['logs']['id'] = channel_id
        self.saveDatabase()
        await self.loadLogsChannel()

    def getUserPerms(self, user):
        lvls = [0]
        for pLvl, pRoles in db['permRoles'].items():
            if any([role.id in pRoles for role in user.roles]):
                lvls.append(int(pLvl))
        permLevel = max(lvls)
        if permLevel == 0 and self.debugging: return -1
        return permLevel

    async def checkPerms(self, message, command):
        perm_lvl = self.getUserPerms(message.author)
        if self.debugging and perm_lvl == -1: 
            await message.reply("Can't use commands while bot is in debugging mode.")
            return False
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

    def getMeEmbed(self, message, user = None):
        embed = dc.Embed(title="User info")
        if not user:
            user = message.author
        embed.color = user.color
        embed.set_image(url=self.getAvatarURL(user))

        joined_info = f"Joined server on `{user.joined_at.strftime('%d/%m/%Y')}`"
        joined_info += f"\nBeen here for: `{str(dt.datetime.now() - user.joined_at).split(',')[0]}`"

        user_roles = [role.mention for role in user.roles if role.name != "@everyone"]
        if not any(user_roles):
            roles_info = "No roles to see here!"
        else:
            roles_info = ", ".join(user_roles)

        # ranking_info =

        embed.add_field(name="Join Date", value=joined_info, inline=False)
        embed.add_field(name="User Roles", value=roles_info, inline=False)
        # embed.add_field(name="Ranking", value=ranking_info, inline=False)
        return embed

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

    async def log(self, message):
        case = db['logs']['cases']
        db['logs']['cases'] = case+1
        self.saveDatabase()

        embed = dc.Embed(title=f"Log Case #{case}")
        embed.color = message.author.color

        embed.add_field(name="Author", value=message.author.mention, inline=True)
        embed.add_field(name="Date", value=dt.datetime.now().strftime("%d/%m/%Y %H:%M:%S"), inline=True)

        embed.add_field(name="Command", value=f"`{message.content}`", inline=False)
        await self.logsChannel.send(embed=embed)

    async def newSemester(self, message, role_template="- Gr "): #zmienna semesters - licznik newSemów
        # później trzeba dodać liczenie kanałów, żeby ewentualnie usuwał niepotrzebne/najstarsze
        # Trzeba najpierw przenosić kanały, dopiero usuwać kategorie
        # if czy jest już kanał o tej nazwie
        print("NEW SEM PRINT")
        arch_category_name = f'sem-{db["semesters"]}-archive'
        await dc.Guild.create_category(name=arch_category_name, position=-1) # ciekawe czy zadziała -1
        # domyślnie dc tworzy kategorię na samym dole, może nie trzeba -1
        await dc.Guild.create_role(name=arch_category_name, add_reactions=False, read_messages=True,send_messages=False, manage_roles=False)
        await dc.CategoryChannel.set_permissions()
        tmp = 0
        all_channels = dc.Guild.channels
        list_channels = [x for x in all_channels if x.endswith('global') or x.endswith('daty-linki') or x.startswith('matma')]
        #to wyżej musisz koniecznie sprawdzić, pewnie tu dużo dziur zostawiłem albo można to uprościć
        channel_amount = len(list_channels)
        roles = await dc.Guild.roles() # The first element of this list will be the lowest role in the hierarchy.
        roles_deletable = [y for y in roles if y.startswith(role_template) or y.startswith('MAT Gr.')]
        while tmp <= list_channels: # nie jestem pewny czy <= czy <
            # tmp = list index
            await list_channels[tmp].edit(sync_permissions=True, position=channel_amount+1, reason=arch_category_name)
            channel_amount+=1
            tmp+=1
        # dobra czyli wszystkie kanały przeniesione na sam dół w takiej kolejnośći jak były
        # omatko trzeba jeszcze pododawać role, dodać rolę archiwum
        # zmiana kanału do logów
        db["semesters"]+=1
        with open(database_relative_path, mode="w") as f:
            json.dump(db, f, indent=4) #cokolwiek indent=4 robi, wzięte z setPrefix
                        

bot_client = BOT()
bot_client.run(token)