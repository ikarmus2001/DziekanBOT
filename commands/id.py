async def user_id(message, args):
    if len(args) == 1:
        if len(message.role_mentions) == 1:
            await message.channel.send(f"id: `{message.role_mentions[0].id}`")
        elif len(message.channel_mentions) == 1:
            await message.channel.send(f"id: `{message.channel_mentions[0].id}`")
        elif len(message.mentions) == 1:
            await message.channel.send(f"id: `{message.mentions[0].id}`")
