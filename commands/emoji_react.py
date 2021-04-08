import asyncio
import string
from collections import Counter
from itertools import chain
import emoji
from discord import Message, PartialMessage, NotFound, Forbidden, HTTPException
from discord.ext.commands import Cog, command


class EmojiReact(Cog):
    letter_emoji_mapping = {
        char: emoji.emojize(f":regional_indicator_{char}:", use_aliases=True)
        for char in string.ascii_lowercase
    }

    space_emoji = emoji.emojize(":black_small_square:", use_aliases=True)

    def valid_message(self, message):
        return all(
            chain(
                map(lambda x: x == 1, Counter(message).values()),
                map(lambda x: x in self.letter_emoji_mapping, message),
            )
        )

    @command(name="say_emoji")
    async def say_emoji(self, ctx: Message, *message_words):
        emoji_message = self.space_emoji.join(
            map(
                lambda word: " ".join(
                    [
                        emoji_substitute
                        for char in word
                        if (
                            emoji_substitute := self.letter_emoji_mapping.get(
                                char, False
                            )
                        )
                    ]
                ),
                message_words,
            )
        )
        await asyncio.gather(ctx.channel.send(emoji_message), ctx.message.delete())

    @command(name="emoji_react")
    async def handle_message(self, ctx: Message, *args):
        message = "".join(args).lower()

        if not self.valid_message(message):
            await ctx.reply("Invalid message")
        elif not ctx.message.reference:
            await ctx.reply("You need to reply to sth")
        else:
            try:
                original_message = await PartialMessage(
                    channel=ctx.channel,
                    id=ctx.message.reference.message_id,
                ).fetch()
            except (NotFound, Forbidden, HTTPException):
                await ctx.reply("Error while fetching original message")
            else:
                deleting_message = asyncio.create_task(ctx.message.delete())

                for x in message:
                    await original_message.add_reaction(self.letter_emoji_mapping[x])
                await deleting_message
