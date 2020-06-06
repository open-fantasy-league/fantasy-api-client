import logging
import os

import dotenv
from discord.ext import commands


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

dotenv.load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
COMMAND_PREFIX = '!'
# TODO @ThePianoDentist
HELP = 'who to contact for more info,\n a sort of faq'

if not BOT_TOKEN:
    print('No bot token found, check .env')
    exit()


bot = commands.Bot(command_prefix=COMMAND_PREFIX, case_insensitive=True,
    description=HELP)

# @JK listeners youll want for logging
# Context object docs - https://discordpy.readthedocs.io/en/latest/ext/commands/api.html#context

# NB these 3 are all listeners specifcaly for command extensions.
# You can also use all the other listenrs defined for client
# https://discordpy.readthedocs.io/en/latest/api.html#event-reference

@bot.event
async def on_command_error(ctx, error):
    """An error handler that is called when an error is raised inside a command either through user input error, check failure, or an error in your own code.

    A default one is provided (Bot.on_command_error())
    """
    await bot.on_command_error(ctx, error)

@bot.event
async def on_command(ctx):
    """An event that is called when a command is found and is about to be invoked.

    This event is called regardless of whether the command itself succeeds via error or completes.
    """
    # eg
    logger.info(f'{ctx.author.name} called {ctx.command.qualified_name} with {ctx.args[2:]}')

@bot.event
async def on_command_completion(ctx):
    """An event that is called when a command has completed its invocation.

    This event is called only if the command succeeded, i.e. all checks have passed and the user input it correctly.
    """ 
    logger.info(f'{ctx.command.qualified_name} called by {ctx.author.name} completed')

@bot.command()
async def reload(ctx):
    bot.reload_extension('fantasydota')
    bot.reload_extension('dev')

bot.load_extension('fantasydota')
bot.load_extension('dev')
bot.run(BOT_TOKEN)
