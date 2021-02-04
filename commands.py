# from bot_class import db
# import discord as dc
# import datetime as dt
from dotenv import load_dotenv
from os import getenv
import json


def loadingAssets():
    load_dotenv()

    # *#*#*# variables #*#*#*#
    config_relative_path = getenv("CONFIG")
    database_relative_path = getenv("DATABASE")
    token = getenv("TOKEN")
    # *#*#*#*#*#*#*#*#*#*#*#*#

    with open(config_relative_path) as f1:
        cfg = json.load(f1)

    with open(database_relative_path) as f2:
        db = json.load(f2)

    return db, cfg, token


def getUserPerms(self, user):
    lvls = [0]
    for permLvl in db['rolePerms']:
        if any([role.id in permLvl.values() for role in user.roles]):
            lvls.append(int(list(permLvl.keys())[0]))
    return max(lvls)


def checkPerms(self, user, perm_lvl):
    return self.getUserPerms(user) >= perm_lvl


def getAvatarURL(self, user):
    base = "https://cdn.discordapp.com/avatars/"
    return base + str(user.id) + "/" + str(user.avatar)


def setPrefix(self, new_prefix, cfg):
    cfg["prefix"] = new_prefix
    with open(config_relative_path, mode="w") as dbfile:
        json.dump(cfg, dbfile)
    self.prefix = new_prefix


def getLeaderboard(self, guild, lenght=5):
    ranking = db["ranking"]
    ranking.sort(key=lambda x: x["exp"], reverse=True)
    lb = ""
    r = 1
    for i in range(min(len(ranking), lenght, 15)):
        user = ranking[i]
        if not guild.get_member(user['id']):
            lb += f"#{r} {guild.get_member(user['id'])}: {user.get('exp')}\n"
            r += 1
    print(lb)
    return lb
