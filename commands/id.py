from typing import Union
from discord import Role, TextChannel, User, Message
from discord.ext.commands import command

mentioned = Union[Role, TextChannel, User]


@command(name="id")
async def user_id(mess: Message, entity: mentioned):
    await mess.reply(entity.id)
