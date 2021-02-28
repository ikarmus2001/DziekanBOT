from discord.ext.commands import command
from .converters.range import RangeConverter


@command(name="purge")
async def purge(ctx, number_messages_to_delete: RangeConverter(1, 50)):
    await ctx.channel.purge(limit=number_messages_to_delete, bulk=True)
