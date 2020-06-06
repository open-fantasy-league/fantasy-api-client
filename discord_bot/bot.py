import asyncio
import logging
import os

import dotenv
from discord.ext import commands

from discord_bot.listener import PlayerHandler, FantasyHandler


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

class FantasyBot(commands.Bot):

    async def connect_clients(self):
        # Bot has a member start had to change name, not sure we are doign here to give good name...
        logger.info("fantasy bot connect clients enter")
        self.player_handler = PlayerHandler()
        self.fantasy_handler = FantasyHandler()
        await asyncio.gather(self.player_handler.start(), self.fantasy_handler.start())
        return 42

    async def on_ready(self):
        logging.info(f'fantasy bot on ready entered')

    # @JK listeners youll want for logging
    # Context object docs - https://discordpy.readthedocs.io/en/latest/ext/commands/api.html#context

    # NB these 3 are all listeners specifcaly for command extensions.
    # You can also use all the other listenrs defined for client
    # https://discordpy.readthedocs.io/en/latest/api.html#event-reference
    async def on_command_error(self, ctx, error):
        """An error handler that is called when an error is raised inside a command either through user input error, check failure, or an error in your own code.

        A default one is provided (Bot.on_command_error())
        """
        await super().on_command_error(ctx, error)

    async def on_command(self, ctx):
        """An event that is called when a command is found and is about to be invoked.

        This event is called regardless of whether the command itself succeeds via error or completes.
        """
        # eg
        logger.info(f'{ctx.author.name} called {ctx.command.qualified_name} with {ctx.args[2:]}')

    async def on_command_completion(self, ctx):
        """An event that is called when a command has completed its invocation.

        This event is called only if the command succeeded, i.e. all checks have passed and the user input it correctly.
        """ 
        logger.info(f'{ctx.command.qualified_name} called by {ctx.author.name} completed')


bot = FantasyBot(command_prefix=COMMAND_PREFIX, case_insensitive=True,
    description=HELP)

# pre connect to discord stuff
asyncio.run(bot.connect_clients())

@bot.command()
async def reload(ctx):
    bot.reload_extension('fantasydota')
    bot.reload_extension('dev')

bot.load_extension('fantasydota')
bot.load_extension('dev')
bot.run(BOT_TOKEN)
