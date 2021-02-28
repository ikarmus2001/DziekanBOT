from discord.ext.commands.errors import BadArgument
from discord.ext.commands.converter import Converter


class PolishBool(Converter):
    yes = {'yes', 'y', 'true', 't', '1', 'enable', 'on', 'tak', 'tag', 'prosz', 'proszem', 'prosze','plz','pls','blagam'}
    no = {'no', 'n', 'false', 'f', '0', 'disable', 'off', 'stop', 'nei', 'nie'}

    async def convert(self, ctx, argument):
        if argument in PolishBool.yes:
            return True
        if argument in PolishBool.no:
            return False
        raise BadArgument

    @staticmethod
    def display():
        return f"Yes | No"
