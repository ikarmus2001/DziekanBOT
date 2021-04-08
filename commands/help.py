from itertools import chain
from discord import User, TextChannel, Role, Member
from discord.partial_emoji import PartialEmoji
import discord
from discord.ext.commands import command
from typing import Union


def arg_to_str(argtype):
    print(type(argtype), argtype.name)

    if argtype is Role:
        return "Role mention"

    if argtype is TextChannel:
        return "Text channel mention"

    if argtype is User:
        return "User mention"

    if argtype is Member:
        return "Member mention"

    if argtype.annotation is PartialEmoji:
        return "Emoji"

    if annotation := getattr(argtype, "annotation", False):
        if callable(getattr(annotation, "display", False)):
            return argtype.annotation.display()

        if getattr(argtype, "__origin__", None) is Union:
            if len(annotation.__args__) == 2 and annotation.__args__[1] is type(None):
                return "Optional " + arg_to_str(argtype.annotation.__args__[0])
            return " | ".join(
                arg_to_str(annotation) for annotation in annotation.__args__
            )

    return f" Couldn't resolve type hint "


def get_command_name(input_command):
    if len(input_command.aliases) > 0:
        return (
            "[ " + " | ".join(chain([input_command.name], input_command.aliases)) + " ]"
        )
    return input_command.name


def get_readable_signature(input_command):
    result = get_command_name(input_command)
    args = [arg_to_str(value) for name, value in input_command.clean_params.items()]

    if len(args) > 0:
        result += f' [ {"".join(args)} ]'
    return result


@command(name="help")
async def dsc_help(ctx):
    embed = discord.Embed(
        title="",
        url="https://github.com/ikarmus2001/DziekanBOT/",
        description="Dziekanbot jest open-sourcowym discordowym botem stworzonym do zarzadzania 'uczelnianym' serverem discorda",
        color=0xFF0000,
    )

    embed.set_author(
        name="DziekanBOT - dostepne komendy",
        url="https://github.com/ikarmus2001/DziekanBOT/",
    )

    for name, value in ctx.bot.all_commands.items():
        embed.add_field(
            name=ctx.prefix + get_readable_signature(value),
            value=value.description or "Lack of documentation",
            inline=False,
        )

    await ctx.message.reply(embed=embed)
