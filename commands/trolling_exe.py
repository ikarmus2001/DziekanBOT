async def trollingDm(user_id, content, public_shaming=False, channel_id=None):
    if not public_shaming:
    if public_shaming == False:
        dm_id = await discord.User.dm_channel(user_id)
        if dm_id is None:
        if dm_id == None:
            dm_id = await discord.User.create_dm()
        await discord.DMChannel.send(content=content, allowed_mentions=True)

    else:
        await message.channel.send(content=content)
