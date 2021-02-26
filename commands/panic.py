import asyncio
import sqlite3
from itertools import chain
from .converters.polish_bool import PolishBool
from discord.ext.commands import command, Cog


class Panic(Cog):
    def __init__(self):
        self.db = sqlite3.connect("panic.db", detect_types=sqlite3.PARSE_DECLTYPES)
        self.db.execute(
            "CREATE TABLE IF NOT EXISTS user_id_mapping (id varchar(50), displayed_username varchar(50))"
        )

    @staticmethod
    async def change_member_nick(member, username):
        try:
            await member.edit(nick=username)
        except:
            pass

    @command(name="paniczka")
    async def panic(self, ctx, to_panic_or_not_to_panic: PolishBool):
        async with asyncio.Lock():
            if to_panic_or_not_to_panic:
                if self.db.execute(
                        "SELECT count(*) != 0 FROM user_id_mapping"
                ).fetchone()[0]:
                    await ctx.message.reply("AAAAAAAAa ty 2 paniczki z rzedu")
                    return

                users = [member async for member in ctx.guild.fetch_members()]

                self.db.executemany(
                    "INSERT INTO user_id_mapping VALUES (?,?)",
                    [(member.id, member.display_name) for member in users],
                )
                self.db.commit()

                await asyncio.wait(
                    chain(
                        [
                            Panic.change_member_nick(member, username)
                            for username, member in enumerate(users)
                        ],
                        *[[channel.send(gif) for gif in
                           ctx.bot.config.start_panic_gifs(ctx.bot.config.gif_per_channel)]
                          for channel in
                          ctx.guild.text_channels]),
                )

            else:
                await asyncio.wait(
                    chain(
                        [
                            Panic.change_member_nick(await ctx.guild.fetch_member(member_id), username)
                            for member_id, username in self.db.execute(
                            "SELECT * FROM user_id_mapping"
                        )
                        ],
                        [ctx.message.reply(gif) for gif in ctx.bot.config.start_panic_gifs(2)],
                    )
                )

                self.db.execute("DELETE FROM user_id_mapping")
                self.db.commit()
