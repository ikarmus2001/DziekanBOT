from discord.ext.commands.errors import BadArgument
from discord.ext.commands.converter import Converter


class RangeConverter(Converter):
    def __init__(self, min_num, max_num):
        self.min_num = min_num
        self.max_num = max_num

    async def convert(self, ctx, argument):
        try:
            num = int(argument)
        except ValueError:
            raise BadArgument
        if self.max_num >= num >= self.min_num:
            return num
        raise BadArgument

    def display(self):
        return f"[{self.min_num}-{self.max_num}]"

