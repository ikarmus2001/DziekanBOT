import discord as dc
from dotenv import load_dotenv
from os import getenv
import datetime as dt
import json
import string
from joachim.db import joachim_db
from joachim.joachin_messages import JoachimMessages
from datetime import datetime


load_dotenv()

# *#*#*# variables #*#*#*#
config_relative_path = getenv("CONFIG")
database_relative_path = getenv("DATABASE")
token = getenv("TOKEN")
# *#*#*#*#*#*#*#*#*#*#*#*#


with open(config_relative_path) as f:
    cfg = json.load(f)
with open(database_relative_path) as f:
    db = json.load(f)


class BOT(dc.Client):
    def __init__(self, intents=None, *args, **kwargs):
        super().__init__(*args, **kwargs, intents=intents)
        self.prefix = cfg["prefix"]
        self.perms = cfg["perms"]
        self.debugging = db["debugMode"]
        # Joachim setup
        self.db = joachim_db()
        self.mess = JoachimMessages(self.db)

    async def on_ready(self):
        for guild in self.guilds:
            print(f"{self.user} connected to {guild.name}, id: {guild.id}")
        print(f"{self.user.name} is alive!")

    async def on_message(self, message):

        if message.author == self.user:
            return
        elif (
            db["groupReg"]["active"]
            and message.channel.id == db["groupReg"]["channel_id"]
        ):
            mess = message.content.lower()

            if "lab" in mess or "mat" in mess:
                await self.groupReg(message)

        elif message.content.startswith(self.prefix):
            await self.command(message)
        elif (self.user.name + " ssie") in message.content or (
            self.user.name + " sucks"
        ) in message.content:
            await message.reply("૮( ᵒ̌▱๋ᵒ̌ )ა ?!")

    async def command(self, message):
        content = message.content[len(self.prefix) :]
        args = content.split()[1::] if len(content.split()) > 1 else [None]
        command = content.split()[0]

        # Joachim overview
        if command.startswith("overview"):

            if "pdp" in args:
                val = self.db.overview("pdp")
                mess_type = "pdp"
            elif "rasberry" in args:
                val = self.db.overview("ras")
                mess_type = "ras"
            elif "japonce" in args:
                val = self.db.overview("jap")
                mess_type = "jap"

            await message.reply(self.mess.overview_message(mess_type, val))

        # Jochaim alerts
        # To do 
        # sprawdzic czy aktualnie odbywaja sie zajecia
        # zrobic ładny wykres ?
        # dodac system losowania wiadomosci podczas alertow
        if command.startswith("alert"):
            if "pdp" in args:
                self.db.alert("pdp")
                await message.reply(self.mess.pdp_message())

            elif "rasberry" in args:
                self.db.alert("ras")
                await message.reply(self.mess.rasberry_message())

            elif "japonce" in args:
                self.db.alert("jap")
                await message.reply(self.mess.jap_message())

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
                    if self.logsActive:
                        await self.log(message)
                else:
                    await message.reply(
                        "Purge amount must be in range from `1` to `50`."
                    )


        # user info embed getter
        elif command == "me" and await self.checkPerms(message, "me"):
            if len(message.mentions) == 1:
                await message.channel.send(
                    embed=self.getMeEmbed(message, message.mentions[0])
                )
            else:
                await message.channel.send(embed=self.getMeEmbed(message))

        # role/channel ID getter
        elif command == "id" and await self.checkPerms(message, "id"):
            if len(args) == 1:
                if len(message.role_mentions) == 1:
                    await message.channel.send(f"id: `{message.role_mentions[0].id}`")
                elif len(message.channel_mentions) == 1:
                    await message.channel.send(
                        f"id: `{message.channel_mentions[0].id}`"
                    )
                elif len(message.mentions) == 1:
                    await message.channel.send(f"id: `{message.mentions[0].id}`")

        # avatar getter
        elif (
            command == "avatar"
            or command == "av"
            and await self.checkPerms(message, "avatar")
        ):
            if message.mentions:
                avatar_url = self.getAvatarURL(message.mentions[0])
            else:
                avatar_url = self.getAvatarURL(message.author)
            await message.reply(avatar_url)

        # perms getter/setter
        elif (
            command == "perms"
            or command == "permissions"
            and await self.checkPerms(message, "permissions")
        ):
            if (
                args[0] == "set"
                and len(args) == 3
                and await self.checkPerms(message, "permissions_manage")
            ):
                try:
                    lvl = int(args[2])
                    if len(message.role_mentions) == 1:
                        role_id = message.raw_role_mentions[0]
                    else:
                        role_id = args[1]
                except:
                    await message.reply(
                        f"Please specify a permission level and role to assign the permission to."
                    )
                else:
                    if lvl not in range(1, 3):
                        await message.reply("Perms level can only be 1 or 2")
                    else:
                        if self.managePerms("set", level=lvl, role=role_id):
                            await message.reply("Role permission changed successfully")
                            if self.logsActive:
                                await self.log(message)
                        else:
                            await message.reply(
                                "Error occured while changing role permissions."
                            )

            elif (args[0] == "delete" or args[0] == "del") and await self.checkPerms(
                message, "permissions_manage"
            ):
                if len(args) == 2:
                    if len(message.role_mentions) == 1:
                        role_id = message.raw_role_mentions[0]
                    else:
                        role_id = args[1]
                    if self.managePerms("delete", role=role_id):
                        if self.logsActive:
                            await self.log(message)
                        await message.reply("Role permission deleted successfully")
                    else:
                        await message.reply(
                            "Error occured while deleting role permissions."
                        )
                else:
                    await message.reply(
                        f"Please specify a role to delete the permission from."
                    )


            elif not any(args):
                perm_lvl = self.getUserPerms(message.author)
                await message.reply(
                    f"Your permission level: `{perm_lvl if perm_lvl < 3 else 'GOD'}`"
                )

        # bot prefix setter
        elif command == "prefix" and await self.checkPerms(message, "prefix"):
            if args[0]:
                self.setPrefix(args[0])
                await message.channel.send(f"Prefix successfully set to: `{args[0]}`")
                if self.logsActive:
                    await self.log(message)

        # leaderboard getter
        elif command == "leaderboard" and await self.checkPerms(message, "leaderboard"):
            lb_len = 5
            if args[0]:
                try:
                    lb_len = int(args[0])
                except:
                    await message.reply(
                        f"Please specify the leaderboard lenght like: `{self.prefix}leaderboard 10`"
                    )
            lb = self.getLeaderboard(message.guild, lb_len)
            await message.channel.send(lb)

        # debug mode
        elif (command == "debug" or command == "debugging") and await self.checkPerms(
            message, "debugging"
        ):
            if args[0] == "on" or args[0] == "true" or args[0] == "1":
                if self.debugging:
                    await message.reply("Debugging mode is already `on`")
                else:
                    self.debugging = db["debugMode"] = True
                    self.saveDatabase()
                    if self.logsActive:
                        await self.log(message)
                    await message.reply(
                        "Debugging mode has been successfully turned `on`"
                    )


            elif args[0] == "off" or args[0] == "false" or args[0] == "0":
                if not self.debugging:
                    await message.reply("Debugging mode is already `off`")
                else:
                    self.debugging = db["debugMode"] = False
                    self.saveDatabase()
                    if self.logsActive:
                        await self.log(message)
                    await message.reply(
                        "Debugging mode has been successfully turned `off`"
                    )

        # logs management
        elif command == "logs" and await self.checkPerms(message, "logs"):
            if args[0] == "set":
                if len(args) == 2 and len(message.channel_mentions) == 1:
                    await self.setLogsChannel(message.channel_mentions[0].id)
                    await message.reply(
                        f"Logs channel successfully set to {message.channel_mentions[0].mention}"
                    )
                else:
                    await message.reply(
                        f"Please specify a log channel like: `{self.prefix}logs set #someLogsChannel`"
                    )
            elif len(args) == 1 and (
                args[0] == "on" or args[0] == "true" or args[0] == "1"
            ):
                self.logsActive = True
                db["logs"]["active"] = True
                self.saveDatabase()
                if self.logsActive:
                    await self.log(message)
                await message.reply("Logs are now turned `on`")
            elif len(args) == 1 and (
                args[0] == "off" or args[0] == "false" or args[0] == "0"
            ):
                if self.logsActive:
                    await self.log(message)
                self.logsActive = False
                db["logs"]["active"] = False
                self.saveDatabase()
                await message.reply("Logs are now turned `off`")

        # semester management
        elif (command == "semester" or command == "sem") and await self.checkPerms(
            message, "semester_manage"
        ):
            if args[0] == "new" or args[0] == "start":
                if not db["groupReg"]["active"]:
                    try:
                        group_count = int(args[1])
                    except:
                        await message.reply(
                            f"Please specify the number of groups like: `{self.prefix}semester new 8`"
                        )
                    else:
                        if await self.openGroupReg(message, group_count):
                            await message.reply("New semester started successfully!")
                            if self.logsActive:
                                await self.log(message)
                        else:
                            await message.reply(
                                "An error has occured while creating new semester."
                            )
                else:
                    await message.reply("Group registration is already open!")
            elif args[0] == "close" or args[0] == "end":
                if db["groupReg"]["active"]:
                    await self.closeGroupReg(message)
                    if self.logsActive:
                        await self.log(message)
                    await message.reply(
                        "Group registration has successfully been closed."
                    )
                else:
                    await message.reply(
                        "There's no group registration currently ongoing to close!"
                    )

    # *=*=*=*=*=*=*=*=* COMMANDS *=*=*=*=*=*=*=*=* #

    def saveDatabase(self):
        with open(database_relative_path, mode="w") as f:
            json.dump(db, f, indent=4)

    async def loadLogsChannel(self):
        channel = await self.fetch_channel(db['logs']['id'])

        if channel:
            self.logsChannel = channel
            self.logsActive = db["logs"]["active"]
        else:
            self.logsActive = db["logs"]["active"] = False
            self.saveDatabase()
            print("Logs channel could not be found by id -- Logs were turned off.")

    async def setLogsChannel(self, channel_id):
        db["logs"]["id"] = channel_id
        self.saveDatabase()
        await self.loadLogsChannel()

    def getUserPerms(self, user):
        lvls = [0]
        for pLvl, pRoles in db["permRoles"].items():
            if any([role.id in pRoles for role in user.roles]):
                lvls.append(int(pLvl))
        permLevel = max(lvls)
        if permLevel == 0 and self.debugging:
            return -1
        return permLevel

    async def checkPerms(self, message, command):
        perm_lvl = self.getUserPerms(message.author)
        if self.debugging and perm_lvl == -1:
            await message.reply("Can't use commands while bot is in debugging mode.")
            return False
        try:
            required = cfg["perms"][command]
        except:
            required = float("infinity")
        if self.getUserPerms(message.author) >= required:
            return True
        else:
            await message.reply("You don't have the permission to use this command.")
            return False

    def getAvatarURL(self, user):
        base = "https://cdn.discordapp.com/avatars/"
        return base + str(user.id) + "/" + str(user.avatar)

    def getMeEmbed(self, message, user=None):
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


    def getLeaderboard(self, guild, length=5):

        ranking = db["ranking"]
        ranking.sort(key=lambda x: x["exp"], reverse=True)
        lb = ""
        r = 1

        for i in range(min(len(ranking), length, 15)):
            user = ranking[i]
            if not guild.get_member(user['id']):

                lb += f"#{r} {guild.get_member(user['id'])}: {user.get('exp')}\n"
                r += 1
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
                        db["permRoles"][pLvl] = [
                            r for r in db["permRoles"][pLvl] if r != role
                        ]
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
                        db["permRoles"][pLvl] = [
                            r for r in db["permRoles"][pLvl] if r != role
                        ]
                        self.saveDatabase()
                        return True
                return False

    async def log(self, message, custom=False):
        if not custom:

            case = db['logs']['cases']
            db['logs']['cases'] = case + 1
            self.saveDatabase()

            embed = dc.Embed(title=f"Log Case #{case}")
            embed.color = message.author.color

            embed.add_field(name="Author", value=message.author.mention, inline=True)
            embed.add_field(name="Channel", value=message.channel.mention, inline=True)
            embed.add_field(
                name="Date",
                value=dt.datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                inline=True,
            )

            embed.add_field(name="Command", value=f"`{message.content}`", inline=True)
            await self.logsChannel.send(embed=embed)
        else:
            await self.logsChannel.send(message)

    async def resetGroupRoles(self, channel, group_count):
        role_template = cfg["nameSpace"]["labRoleTemplate"].split("#")
        math_role_template = cfg["nameSpace"]["mathRoleTemplate"].split("#")
        if len(role_template) != 2:
            print("config group role template invalid: missing '#'?")
            return False
        elif len(math_role_template) != 2:
            print("config math group role template invalid: missing '#'?")
            return False
        # initialize flags to see which roles exist and create the nonexistent ones later
        lab_flags = [0 for _ in range(group_count)]
        mat_flags = [0 for _ in range((group_count - 1) // 2 + 1)]

        records = {}  # keep record of removed data to save and log it later
        for role in await channel.guild.fetch_roles():
            if (
                role.name.startswith(role_template[0])
                and role.name.endswith(role_template[1])
            ) or (
                role.name.startswith(math_role_template[0])
                and role.name.endswith(math_role_template[1])
            ):

                role_type = "LAB" if role.name.startswith(role_template[0]) else "MAT"
                records[str(role.name)] = []
                members = role.members
                # g_id determines the current group's number
                if role_type == "LAB":
                    g_id = int(
                        role.name[len(role_template[0]) : -len(role_template[1])]
                    )
                elif role_type == "MAT":
                    g_id = int(
                        role.name[
                            len(math_role_template[0]) : -len(math_role_template[1])
                        ]
                    )

                # clear role from every user and store the changes in records
                await channel.send(
                    f"Clearing `{role.name}` from `{len(members)}` users.."
                )
                for member in members:
                    records[role.name].append(
                        str(member.name + "#" + member.discriminator)
                    )
                    await member.remove_roles(role)

                # remove the role entirely if it's not in range of new semester's group length
                if g_id not in range(1, group_count + 1):
                    await channel.send(f"Removing `{role.name}`..")
                    await role.delete()
                elif role_type == "MAT" and g_id not in range(1, len(mat_flags) + 1):
                    await channel.send(f"Removing `{role.name}`..")
                    await role.delete()
                else:
                    # set flags for roles kept for next semester and save their id's in db for future registration management
                    if role_type == "LAB":
                        lab_flags[g_id - 1] = 1
                        db["groupReg"]["role_ids"][str(g_id)] = role.id
                    elif role_type == "MAT":
                        mat_flags[g_id - 1] = 1
                        db["groupReg"]["math_role_ids"][str(g_id)] = role.id

        self.saveDatabase()

        # create nonexistent roles based on gaps in flags
        for ID, flag in enumerate(lab_flags):
            if not flag:
                name = f"{role_template[0]}{ID + 1}{role_template[1]}"
                await channel.send(f"Creating `{name}`..")
                role = await channel.guild.create_role(
                    name=name, mentionable=True, hoist=True, color=dc.Color.random()
                )

                db["groupReg"]["role_ids"][str(ID + 1)] = role.id
        for ID, flag in enumerate(mat_flags):
            if not flag:
                name = f"{math_role_template[0]}{ID + 1}{math_role_template[1]}"
                await channel.send(f"Creating `{name}`..")
                role = await channel.guild.create_role(
                    name=name, mentionable=True, color=dc.Color.random()
                )

                db["groupReg"]["math_role_ids"][str(ID + 1)] = role.id

        self.saveDatabase()

        # save records to file and log them to logs channel if active
        with open("archives.txt", "a") as f:
            json.dump(records, f, indent=4)
        # if self.logsActive:
        #     await self.log(f'```json\n{json.dumps(records,indent=4)}\n```', custom=True)
        #     await channel.send(f'`Archive sent to logs channel and saved on machine.`')
        # else:
        await channel.send(f"`Archive saved on machine.`")
        return True

    async def openGroupReg(self, message, group_count):
        if await self.resetGroupRoles(message.channel, group_count):
            db["groupReg"]["active"] = True
            db["groupReg"][
                "groupCount"
            ] = group_count  # group_count determines the len of lab groups in new semester
            # rid of registration category and text channels if they exist
            for category in message.guild.categories:
                if category.name == cfg["nameSpace"]["groupsRegCategory"]:
                    for channel in category.channels:
                        await channel.delete()
                    await category.delete()
                    break
            # create new category with its text channels for registration
            GRC = await message.guild.create_category(
                name=cfg["nameSpace"]["groupsRegCategory"], position=2
            )
            GRIC = await GRC.create_text_channel(
                name=cfg["nameSpace"]["groupsRegInfoChannel"]
            )
            await GRIC.set_permissions(
                message.guild.roles[0], send_messages=False, read_messages=True
            )
            GRC = await GRC.create_text_channel(
                name=cfg["nameSpace"]["groupsRegChannel"]
            )

            # save the channel id used for registration for command management purposes
            db["groupReg"]["channel_id"] = GRC.id
            self.saveDatabase()
            # send registration opening notification to GRIC
            await message.channel.send(f"`Group registration channel created.`")
            info = f""":warning: @everyone Rejestracja do grup w nowym semestrze została otwarta! :warning: \n

**Aby poprawnie zarejestrować się do grupy LAB oraz MAT wyślij** `lab #numerGrupy` **oraz** `mat #numerGrupy` **na kanale** {GRC.mention}, np. `lab 4`; `mat 2` lub `lab 4 mat 2`.
Dla osób będących w kilku grupach laboratoryjnych jednocześnie - proszę kontaktować się z administracją serwera."""
            await GRIC.send(info)

            # send new semester decorator on all group channels
            for channel in message.guild.channels:
                if channel.name.endswith(cfg["nameSpace"]["generalChannelTemplate"]):
                    await channel.send(cfg["nameSpace"]["newSemesterDecorator"])
                elif channel.name.endswith(cfg["nameSpace"]["datesChannelTemplate"]):
                    await channel.send(cfg["nameSpace"]["newSemesterDecorator"])
                elif channel.name.startswith(cfg["nameSpace"]["mathChannelTemplate"]):
                    await channel.send(cfg["nameSpace"]["newSemesterDecorator"])
            return True

        return False

    async def groupReg(self, message):
        user = message.author
        content = message.content.lower()


        l_id = content.find('lab')
        m_id = content.find('mat')

        digits = string.digits
        lab_gr = mat_gr = None

        # do some string magic to extract lab group number from message if it inclues "lab" keyword
        if l_id >= 0:
            if m_id > l_id:  # dont include the "mat" keyword if it appears after "lab"

                cntnt = content[l_id + 3 : m_id].lstrip()
            else:
                cntnt = content[l_id + 3 :].lstrip()
            lab_gr = int(
                "".join(
                    [
                        v
                        for vID, v in enumerate(cntnt)
                        if v in digits
                        and not any([c not in digits for c in cntnt[:vID]])
                    ]
                )
            )
            # return with an exception if the number is not in current lab groups range
            if lab_gr not in range(1, db["groupReg"]["groupCount"] + 1):
                await message.reply(
                    f"Lab group needs to be between `1` and `{db['groupReg']['groupCount']}`."
                )
                return
        # same string magic for mat group number
        if m_id >= 0:
            if l_id > m_id:  # dont include the "lab" keyword if it appears after "mat"
                cntnt = content[m_id + 3 : l_id].lstrip()
            else:
                cntnt = content[m_id + 3 :].lstrip()
            mat_gr = int(
                "".join(
                    [
                        v
                        for vID, v in enumerate(cntnt)
                        if v in digits
                        and not any([c not in digits for c in cntnt[:vID]])
                    ]
                )
            )
            # return with an exception if the number is not in current mat groups range
            if mat_gr not in range(1, (db["groupReg"]["groupCount"] - 1) // 2 + 2):
                await message.reply(
                    f"Mat group needs to be between `1` and `{(db['groupReg']['groupCount']-1)//2 + 1}`."
                )
                return

        # assign group roles to user and catch the output
# idk tu mi krzyczy błąd
#                 cntnt = content[l_id + 3:m_id].lstrip()
#             else:
#                 cntnt = content[l_id + 3:].lstrip()
#             lab_gr = int("".join(
#                 [v for vID, v in enumerate(cntnt) if v in digits and not any([c not in digits for c in cntnt[:vID]])]))
#             # return with an exception if the number is not in current lab groups range
#             if lab_gr not in range(1, db["groupReg"]["groupCount"] + 1):
#                 await message.reply(f"Lab group needs to be between `1` and `{db['groupReg']['groupCount']}`.")
#                 return
#                 # same string magic for mat group number
#         if m_id >= 0:
#             if l_id > m_id:  # dont include the "lab" keyword if it appears after "mat"
#                 cntnt = content[m_id + 3:l_id].lstrip()
#             else:
#                 cntnt = content[m_id + 3:].lstrip()
#             mat_gr = int("".join(
#                 [v for vID, v in enumerate(cntnt) if v in digits and not any([c not in digits for c in cntnt[:vID]])]))
#             # return with an exception if the number is not in current mat groups range
#             if mat_gr not in range(1, (db["groupReg"]["groupCount"] - 1) // 2 + 2):
#                 await message.reply(
#                     f"Mat group needs to be between `1` and `{(db['groupReg']['groupCount'] - 1) // 2 + 1}`.")
#                 return

        out = await self.regToGroups(user, lab_gr, mat_gr)
        if out:
            await message.reply(f"Successfully registered to: `{'`, `'.join(out)}`")
        else:
            await message.reply(
                "An error occured while registering to group, please try again."
            )

    async def regToGroups(self, user, labGroup=None, matGroup=None):
        if not (labGroup or matGroup):
            return False
        for role in user.roles:
            if labGroup and role.id in tuple(db["groupReg"]["role_ids"].values()):
                await user.remove_roles(role)
            elif matGroup and role.id in tuple(
                db["groupReg"]["math_role_ids"].values()
            ):
                await user.remove_roles(role)

        output = []  # store successfully applied roles in output
        if labGroup:
            lab_id = db["groupReg"]["role_ids"][str(labGroup)]
            role = user.guild.get_role(lab_id)
            output.append(role.name)
            await user.add_roles(role)
        if matGroup:
            mat_id = db["groupReg"]["math_role_ids"][str(matGroup)]
            role = user.guild.get_role(mat_id)
            output.append(role.name)
            await user.add_roles(role)
        return output

    async def closeGroupReg(self, message):
        # reset group registration database
        db["groupReg"]["active"] = False
        db["groupReg"]["channel_id"] = None
        db["groupReg"]["groupCount"] = 0
        db["groupReg"]["role_ids"] = {}
        db["groupReg"]["math_role_ids"] = {}
        self.saveDatabase()

        # rid of registration category and text channels if they exist
        for category in message.guild.categories:
            if category.name == cfg["nameSpace"]["groupsRegCategory"]:
                for channel in category.channels:
                    await channel.delete()
                await category.delete()
                break


intents = dc.Intents.all()
bot_client = BOT(intents=intents)
bot_client.run(token)
