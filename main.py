import discord
from discord.ext.commands import Bot
from discord.ext.commands.errors import (
    CommandNotFound,
    BadArgument,
    BadUnionArgument,
    MissingRequiredArgument,
)

from commands.help import dsc_help
from commands.id import user_id
from commands.me import me
from commands.panic import Panic
from commands.purge import purge
from commands.emojis_for_poor import EmojisForPoor
from commands.emoji_react import EmojiReact
from commands.say import say
from commands.help import get_readable_signature
from config import Config


# Commands




class CustomBot(Bot):
    def __init__(self, config):
        self.config = config
        self.emojis_for_poor = EmojisForPoor()

        super().__init__(command_prefix="!", intents=discord.Intents.all())
        self.add_cog(self.emojis_for_poor)

    async def on_command_error(self, context, exception):
        if isinstance(exception, CommandNotFound):
            await context.message.reply(
                f"Command doesn't exists try - {self.command_prefix}help"
            )

        elif isinstance(
            exception, (BadArgument, BadUnionArgument, MissingRequiredArgument)
        ):
            await context.message.reply(
                "Error while trying to parse args \n**Correct use ** - "
                + self.command_prefix
                + get_readable_signature(context.command)
            )

        raise exception

    async def on_message(self, message):
        if not await self.emojis_for_poor.message_contains_emoji_attempt(message):
            await self.process_commands(message)


client = CustomBot(Config())

# Object command instances
panic_obc = Panic()
emoji_react = EmojiReact()

client.add_cog(panic_obc)
client.add_cog(emoji_react)


client.add_command(say)
client.add_command(me)
client.add_command(purge)
client.add_command(user_id)

client.remove_command("help")
client.add_command(dsc_help)
