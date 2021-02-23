import sqlite3
import asyncio

import discord as dc

from config import Config

from commands.id import user_id
from commands.me import me
from commands.purge import purge
from commands.say import say
from commands.joachim import Joachim


class Bot(dc.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, intents=dc.Intents.all())
        self.config = Config()

        self.db = sqlite3.connect("db.db", detect_types=sqlite3.PARSE_DECLTYPES)
        self.db.execute(
            "CREATE TABLE IF NOT EXISTS user_id_mapping (id varchar(50), displayed_username varchar(50))"
        )

        self.joachim = Joachim(self.db, self.config)

        self.commands_handlers = {
            "id": user_id,
            "me": me,
            "say": say,
            "purge": purge,
            "panic": self.panic,
            "help": self.help,
            "overview": self.joachim.overview,
            "alert": self.joachim.alert,
        }

    async def panic(self, message, args):
        async with asyncio.Lock():
            if "on" in args:
                user_count  = self.db.execute("SELECT count(*) FROM user_id_mapping").fetchone()[0]

                if user_count != 0:
                    await message.reply("AAAAAAAAa ty 2 paniczki z rzedu")
                    return

                users = [*self.get_all_members()]
                self.db.executemany(
                    "INSERT INTO user_id_mapping VALUES (?,?)",
                    [(user.id, user.display_name) for user in users],
                )
                self.db.commit()

                await message.reply(self.config.start_panic_gif)

                for index, user in enumerate(users):
                    try:
                        await user.edit(nick=index)
                    except:
                        continue

            elif "off" in args:
                await message.reply(self.config.end_panic_gif)

                for member_id, username in self.db.execute(
                    "SELECT * FROM user_id_mapping"
                ):
                    user = await message.guild.fetch_member(member_id)
                    try:
                        await user.edit(nick=username)
                    except:
                        continue
                self.db.execute("DELETE FROM user_id_mapping")
                self.db.commit()
                print("DELETED")

    async def help(self, message, _):
        """Wlasnie to czytasz"""
        dc.embeds.Embed()
        embed = dc.Embed(
            title="",
            url="https://github.com/ikarmus2001/DziekanBOT/",
            description="Dziekanbot jest open-sourcowym discordowym botem stworzonym do zarzadzania 'uczelnianym' serverem discorda",
            color=0xFF0000,
        )
        embed.set_author(
            name="DziekanBOT - dostepne komendy",
            url="https://github.com/ikarmus2001/DziekanBOT/",
        )

        for name, command in filter(
            lambda x: True,
            self.commands_handlers.items(),
        ):
            embed.add_field(
                name=self.config.prefix + name,
                value=command.__doc__
                if command.__doc__ is not None
                else "Brak dokumentacji",
                inline=False,
            )

        await message.reply(embed=embed)

    async def on_ready(self):
        print(f"{self.user.name} is alive!")

    async def on_message(self, message):
        if message.author == self.user:
            return

        if message.content.startswith(self.config.prefix):
            content = message.content[len(self.config.prefix) :]
            args = content.split()[1::] if len(content.split()) > 1 else [None]
            command = content.split()[0]

            if func := self.commands_handlers.get(command, False):
                if await self.config.has_permision(command, message):
                    await func(message, args)
                else:
                    await message.reply("Nie masz permisji aby wykonac ta komende")
            else:
                await message.reply(
                    f"Nie znaleziono komendy help - {self.config.prefix}help"
                )


bot_client = Bot()
bot_client.run(bot_client.config.token)
