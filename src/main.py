from pathlib import Path
import logging
import os
import traceback

from dotenv import load_dotenv
from rich.logging import RichHandler
import discord
from discord.ext import commands


logging.basicConfig(
    level=logging.DEBUG,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler()]
)
logger = logging.getLogger("root")
root_path = Path(__file__).parents[1]
os.chdir(root_path / 'src')
load_dotenv(str(root_path) + "/.secrets")

intents = discord.Intents.all()
intents.message_content = True

bot = commands.Bot(command_prefix='?', description="...", intents=intents)


@bot.event
async def setup_hook():
    try:
        for file in os.listdir(root_path / 'src' / 'cogs'):
            if file.endswith('.py') and file != '__init__.py':
                filename = file[:-3]
                try:
                    await bot.load_extension(f'cogs.{filename}')
                    logging.info(f"{filename} module prepared.")
                except Exception as e:
                    logging.error(f"Failed to load {filename}: {e}")
                    traceback.print_exc()
    except Exception as e:
        logging.error(f"Cog loading error: {e}")
        traceback.print_exc()


@bot.event
async def on_ready():
    logging.info("Tulip is ready. Awaiting instructions...")


@bot.event
async def on_command_error(ctx, error):
    original = getattr(error, 'original', error)

    if isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Missing argument: `{error.param.name}`")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("I couldn't convert one of the arguments.")
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"This command is on cooldown. Try again in {error.retry_after:.1f}s.")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to run that command.")
    elif isinstance(error, commands.CheckFailure):
        await ctx.send("You failed a check required to run this command.")
    else:
        logger.exception(f"Unhandled command error: {original}")
        await ctx.send("Something went wrong. The error has been logged.")


token = os.getenv("API_TOKEN")
bot.run(token)
