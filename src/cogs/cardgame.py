from discord.ext import commands
from cogs.velmoria.core.base import Unit


class Velmoria(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


async def setup(bot):
    await bot.add_cog(Velmoria(bot))
