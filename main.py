import discord
from discord.ext.commands import Bot
from discord.ext.commands.errors import CommandNotFound, BadArgument, BadUnionArgument

from commands.help import dsc_help
from commands.id import user_id
from commands.me import me
from commands.panic import Panic
from commands.purge import purge
from commands.say import say
from commands.help import get_readable_signature
from config import Config


# Commands


# class Bot(dc.Client):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs, intents=dc.Intents.all())
#         self.config = Config()
#

#         self.joachim = Joachim(self.db, self.config)
#
#         self.commands_handlers = {
#             "id": user_id,
#             "me": me,
#             "say": say,
#             "purge": purge,
#             "panic": self.panic,
#             "help": self.help,
#             "overview": self.joachim.overview,
#             "alert": self.joachim.alert,
#             "laby": self.register_to_group,
#         }
#
#     async def register_to_group(self, message, args):
#         try:
#             assert args[0] in self.config.lab_ids
#             assert args[1] == "mat"
#             assert args[2] in self.config.math_ids
#
#             print(dc.Role(self.config.math_ids[args[0]]),
#                   self.config.math_ids[args[2]])
#             await message.author.add_roles(
#                 self.config.math_ids[args[0]],
#                 self.config.math_ids[args[2]]
#             )
#
#         except AssertionError:
#             await message.reply(
#                 f"Uzycie {self.config.prefix}laby [1-{len(self.config.lab_ids)}] mat [1-{len(self.config.math_ids)}]"
#             )
#

#     async def help(self, message, _):
#         """Wlasnie to czytasz"""
#         dc.embeds.Embed()
#         embed = dc.Embed(
#             title="",
#             url="https://github.com/ikarmus2001/DziekanBOT/",
#             description="Dziekanbot jest open-sourcowym discordowym botem stworzonym do zarzadzania 'uczelnianym' serverem discorda",
#             color=0xFF0000,
#         )
#         embed.set_author(
#             name="DziekanBOT - dostepne komendy",
#             url="https://github.com/ikarmus2001/DziekanBOT/",
#         )
#
#         for name, command in filter(
#                 lambda entry: self.config.has_permission(entry[0], message),
#                 self.commands_handlers.items(),
#         ):
#             embed.add_field(
#                 name=self.config.prefix + name,
#                 value=command.__doc__
#                 if command.__doc__ is not None
#                 else "Brak dokumentacji",
#                 inline=False,
#             )
#
#         await message.reply(embed=embed)
#
#     async def on_ready(self):
#         print(f"{self.user.name} is alive!")
#
#     async def on_message(self, message):
#         if message.author == self.user:
#             return
#
#         if message.content.startswith(self.config.prefix):
#             content = message.content[len(self.config.prefix):]
#             args = content.split()[1::] if len(content.split()) > 1 else [None]
#             command = content.split()[0]
#
#             if func := self.commands_handlers.get(command, False):
#                 if self.config.has_permission(command, message):
#                     await func(message, args)
#                 else:
#                     await message.reply("Nie masz permisji aby wykonac ta komende")
#             else:
#                 await message.reply(
#                     f"Nie znaleziono komendy help - {self.config.prefix}help"
#                 )


class CustomBot(Bot):
    def __init__(self, config):
        self.config = config
        super().__init__(command_prefix="!", intents=discord.Intents.all())

    async def on_command_error(self, context, exception):
        if isinstance(exception, CommandNotFound):
            await context.message.reply(f"Command doesn't exists try - {self.command_prefix}help")

        elif isinstance(exception, BadArgument) or isinstance(exception, BadUnionArgument):
            await context.message.reply(
                "Error while trying to parse args \n**Correct use ** - "
                + self.command_prefix + get_readable_signature(context.command))
        raise exception


client = CustomBot(Config())

# Object command instances
panic_obc = Panic()

client.add_command(say)
client.add_command(me)
client.add_command(purge)
client.add_command(user_id)

client.remove_command('help')
client.add_command(dsc_help)

client.add_cog(panic_obc)

client.run("ODEzMzY3NTI3MTYwODA3NDc0.YDORig.te5ohBTOkEGIvVjWWSCC9glw7GA")
