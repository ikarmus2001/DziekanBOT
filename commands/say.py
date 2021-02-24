async def say(message, args):
    await message.delete()
    if any(args):
        await message.channel.send(" ".join([arg for arg in args]))
