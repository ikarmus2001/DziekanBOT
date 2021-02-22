import datetime as dt
import discord as dc


def getAvatarURL(user):
    base = "https://cdn.discordapp.com/avatars/"
    return base + str(user.id) + "/" + str(user.avatar)


async def get_me_embed(message, user=None):
    embed = dc.Embed(title="User info")

    if not user:
        user = message.author

    embed.color = user.color
    embed.set_image(url=getAvatarURL(user))

    joined_info = f"Joined server on `{user.joined_at.strftime('%d/%m/%Y')}`"
    joined_info += f"\nBeen here for: `{str(dt.datetime.now() - user.joined_at).split(',')[0]}`"

    user_roles = [role.name for role in user.roles if role.name != "@everyone"]
    
    if not user_roles:
        roles_info = "No roles to see here!"
    else:
        roles_info = ", ".join(user_roles)

    embed.add_field(name="Join Date", value=joined_info, inline=False)
    embed.add_field(name="User Roles", value=roles_info, inline=False)

    await message.channel.send(embed=embed)


async def me(message, args):
    if len(message.mentions) == 1:
        await get_me_embed(message, message.mentions[0])
    else:
        await get_me_embed(message)

