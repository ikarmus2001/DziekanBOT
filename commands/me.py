import datetime as dt
import discord as dc
from discord import Member, Message
from typing import Optional
from discord.ext.commands import command


def get_avatar_url(user):
    base = "https://cdn.discordapp.com/avatars/"
    return base + str(user.id) + "/" + str(user.avatar)


@command(name='me')
async def me(ctx: Message, user: Optional[Member]):
    user = ctx.author if user is None else user

    embed = dc.Embed(title="User info")
    embed.color = user.color
    embed.set_image(url=get_avatar_url(user))

    joined_info = f"Joined server on `{user.joined_at.strftime('%d/%m/%Y')}`"
    joined_info += (
        f"\nBeen here for: `{str(dt.datetime.now() - user.joined_at).split(',')[0]}`"
    )

    roles_info = ",".join([role.name for role in user.roles if role.name != "@everyone"]) or "No roles to see here!"

    embed.add_field(name="Join Date", value=joined_info, inline=False)
    embed.add_field(name="User Roles", value=roles_info, inline=False)

    await ctx.reply(embed=embed)
