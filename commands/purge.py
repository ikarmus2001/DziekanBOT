async def purge(message, args):
    try:
        del_range = int(args[0])
    except ValueError:
        await message.reply("Please specify how many messages to purge.")
    else:
        if del_range in range(1, 51):
            await message.channel.purge(limit=del_range + 1, bulk=True)
        else:
            await message.reply(
                "Purge amount must be in range from `1` to `50`."
            )


