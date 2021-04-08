from discord.ext.commands import command


@command(name="say")
async def say(ctx):
    await ctx.channel.send(ctx.message.content[5:])
    await ctx.message.delete()
