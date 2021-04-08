import asyncio

from discord import Message, PartialEmoji
from discord.ext.commands import command, Cog
from discord import Embed


class EmojisForPoor(Cog):
    def __init__(self):
        self.emoji_store = {}
        self.available_emojis_message = None

    @command(name="register_emoji")
    async def register_emoji(self, message: Message, emoji: PartialEmoji):
        image = Embed(
            title=f'Emoji "{emoji.name}" added by {message.author.name}', url=emoji.url
        )

        reply = asyncio.create_task(message.reply(embed=image))

        self.emoji_store[emoji.name.lower()] = emoji.url
        self.available_emojis_message = (
            f'Emoji "**{emoji.name}**" not found, available emojis: '
            + ", ".join(map(lambda x: f"**{x}**", self.emoji_store.keys()))
        )

        await reply

    async def message_contains_emoji_attempt(self, message: Message):
        if (emoji := message.clean_content).startswith(":"):
            end_of_emoji_name = emoji.rfind(":")

            if end_of_emoji_name == 0 or end_of_emoji_name == 1:
                return False

            emoji_name = emoji[1:end_of_emoji_name]

            if emoji_url := self.emoji_store.get(emoji_name.lower(), False):
                task = asyncio.create_task(message.delete())
                await message.channel.send(f"Via <@{message.author.id}>")
                await message.channel.send(emoji_url)
                await task
            else:
                await message.reply(self.available_emojis_message)
            return True
        return False
