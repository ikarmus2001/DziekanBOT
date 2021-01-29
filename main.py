import os

import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
client = discord.Client()


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

    for guild in client.guilds:
        if guild.name == GUILD:
            break
    print("{} connected to {}, id: {}".format(client.user, guild.name, guild.id))

    members = '\n - '.join([member.name for member in guild.members])
    print('Guild Members:\n - {}'.format(members))

client.run(TOKEN)
