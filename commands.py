import discord as dc
import datetime as dt
import string
from main import json
from main import db, cfg, joachim
from main import database_relative_path, config_relative_path  # , joachim_relative_path


class Commands(dc.Client):

    def saveDatabase(self):
        with open(database_relative_path, mode="w") as f:
            json.dump(db, f, indent=4)

    async def loadLogsChannel(self):
        try:
            channel = await self.fetch_channel(db['logs']['id'])
            if channel:
                self.logsChannel = channel
                self.logsActive = db['logs']['active']
        except dc.errors.Forbidden:
            self.logsActive = db['logs']['active'] = False
            self.saveDatabase()
            print("\nLogs channel could not be found by id -- Logs were turned off.\n")

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
            required = float('infinity')
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

    async def log(self, message, custom=False):
        if not custom:
            case = db['logs']['cases']
            db['logs']['cases'] = case + 1
            self.saveDatabase()

            embed = dc.Embed(title=f"Log Case #{case}")
            embed.color = message.author.color

            embed.add_field(name="Author", value=message.author.mention, inline=True)
            embed.add_field(name="Channel", value=message.channel.mention, inline=True)
            embed.add_field(name="Date", value=dt.datetime.now().strftime("%d/%m/%Y %H:%M:%S"), inline=True)

            embed.add_field(name="Command", value=f"`{message.content}`", inline=True)
            await self.logsChannel.send(embed=embed)
        else:
            await self.logsChannel.send(message)

    async def resetGroupRoles(self, channel, group_count):
        role_template = cfg["nameSpace"]["labRoleTemplate"].split('#')
        math_role_template = cfg["nameSpace"]["mathRoleTemplate"].split('#')
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
            if (role.name.startswith(role_template[0]) and role.name.endswith(role_template[1])) or (
                    role.name.startswith(math_role_template[0]) and role.name.endswith(math_role_template[1])):
                role_type = "LAB" if role.name.startswith(role_template[0]) else "MAT"
                records[str(role.name)] = []
                members = role.members
                # g_id determines the current group's number
                if role_type == "LAB":
                    g_id = int(role.name[len(role_template[0]):-len(role_template[1])])
                elif role_type == "MAT":
                    g_id = int(role.name[len(math_role_template[0]):-len(math_role_template[1])])

                # clear role from every user and store the changes in records
                await channel.send(f"Clearing `{role.name}` from `{len(members)}` users..")
                for member in members:
                    records[role.name].append(str(member.name + '#' + member.discriminator))
                    await member.remove_roles(role)

                # remove the role entirely if it's not in range of new semester's group length
                if g_id not in range(1, group_count + 1):
                    await channel.send(f"Removing `{role.name}`..")
                    await role.delete()
                elif role_type == "MAT" and g_id not in range(1, len(mat_flags) + 1):
                    await channel.send(f"Removing `{role.name}`..")
                    await role.delete()
                else:
                    # set flags for roles kept for next sem and save their id's in db for future registration management
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
                role = await channel.guild.create_role(name=name, mentionable=True, hoist=True, color=dc.Color.random())
                db["groupReg"]["role_ids"][str(ID + 1)] = role.id
        for ID, flag in enumerate(mat_flags):
            if not flag:
                name = f"{math_role_template[0]}{ID + 1}{math_role_template[1]}"
                await channel.send(f"Creating `{name}`..")
                role = await channel.guild.create_role(name=name, mentionable=True, color=dc.Color.random())
                db["groupReg"]["math_role_ids"][str(ID + 1)] = role.id

        self.saveDatabase()

        # save records to file and log them to logs channel if active
        with open('archives.txt', 'a') as f:
            json.dump(records, f, indent=4)
        # if self.logsActive:
        #     await self.log(f'```json\n{json.dumps(records,indent=4)}\n```', custom=True)
        #     await channel.send(f'`Archive sent to logs channel and saved on machine.`')
        # else:
        await channel.send(f'`Archive saved on machine.`')
        return True

    async def openGroupReg(self, message, group_count):
        if await self.resetGroupRoles(message.channel, group_count):
            db["groupReg"]["active"] = True
            db["groupReg"]["groupCount"] = group_count  # group_count determines the len of lab groups in new semester
            # rid of registration category and text channels if they exist
            for category in message.guild.categories:
                if category.name == cfg["nameSpace"]["groupsRegCategory"]:
                    for channel in category.channels:
                        await channel.delete()
                    await category.delete()
                    break
            # create new category with its text channels for registration
            GRC = await message.guild.create_category(name=cfg["nameSpace"]["groupsRegCategory"], position=2)
            GRIC = await GRC.create_text_channel(name=cfg["nameSpace"]["groupsRegInfoChannel"])
            await GRIC.set_permissions(message.guild.roles[0], send_messages=False, read_messages=True)
            GRC = await GRC.create_text_channel(name=cfg["nameSpace"]["groupsRegChannel"])
            # save the channel id used for registration for command management purposes
            db["groupReg"]["channel_id"] = GRC.id
            self.saveDatabase()

            # send registration opening notification to GRIC
            await message.channel.send(f'`Group registration channel created.`')
            info = f''':warning: @everyone Rejestracja do grup w nowym semestrze została otwarta! :warning: \n
    **Aby poprawnie zarejestrować się do grupy LAB oraz MAT wyślij** `lab #numerGrupy` **oraz** `mat #numerGrupy` **na kanale** {GRC.mention}, np. `lab 4`; `mat 2` lub `lab 4 mat 2`.
    Dla osób będących w kilku grupach laboratoryjnych jednocześnie - proszę kontaktować się z administracją serwera.'''
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
                cntnt = content[l_id + 3:m_id].lstrip()
            else:
                cntnt = content[l_id + 3:].lstrip()
            lab_gr = int("".join(
                [v for vID, v in enumerate(cntnt) if v in digits and not any([c not in digits for c in cntnt[:vID]])]))
            # return with an exception if the number is not in current lab groups range
            if lab_gr not in range(1, db["groupReg"]["groupCount"] + 1):
                await message.reply(f"Lab group needs to be between `1` and `{db['groupReg']['groupCount']}`.")
                return
                # same string magic for mat group number
        if m_id >= 0:
            if l_id > m_id:  # dont include the "lab" keyword if it appears after "mat"
                cntnt = content[m_id + 3:l_id].lstrip()
            else:
                cntnt = content[m_id + 3:].lstrip()
            mat_gr = int("".join(
                [v for vID, v in enumerate(cntnt) if v in digits and not any([c not in digits for c in cntnt[:vID]])]))
            # return with an exception if the number is not in current mat groups range
            if mat_gr not in range(1, (db["groupReg"]["groupCount"] - 1) // 2 + 2):
                await message.reply(
                    f"Mat group needs to be between `1` and `{(db['groupReg']['groupCount'] - 1) // 2 + 1}`.")
                return

                # assign group roles to user and catch the output
        out = await self.regToGroups(user, lab_gr, mat_gr)
        if out:
            await message.reply(f"Successfully registered to: `{'`, `'.join(out)}`")
        else:
            await message.reply("An error occured while registering to group, please try again.")

    async def regToGroups(self, user, labGroup=None, matGroup=None):
        if not (labGroup or matGroup): return False
        for role in user.roles:
            if labGroup and role.id in tuple(db["groupReg"]["role_ids"].values()):
                await user.remove_roles(role)
            elif matGroup and role.id in tuple(db["groupReg"]["math_role_ids"].values()):
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
