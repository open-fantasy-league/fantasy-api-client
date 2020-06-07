import asyncio
import logging
import os
from pprint import pformat

import dotenv
from discord.ext import commands

from discord_bot.listener import PlayerHandler, FantasyHandler


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

dotenv.load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
COMMAND_PREFIX = '!'
# TODO @ThePianoDentist
HELP_COMMAND_TEXT = 'i help you help we help'

if not BOT_TOKEN:
    print('No bot token found, check .env')
    exit()

class FantasyBot(commands.Bot):

    def __init__(self, *args, **kwargs):
        self.player_handler = None
        self.fantasy_handler = None
        # Be careful users is a member of Bot
        self.external_users = None  # not used atm
        super().__init__(*args, **kwargs)

    async def on_ready(self):
        logger.info(f'fantasy bot on ready entered')
        # TOMAYBEDO now that connect clients also sets up listeners think we need to 
        # do something to prevent user commands while bot is setting up
        await self.connect_clients() #  this stays "connected" should mb handle differently
        logger.info(f'fantasy bot on ready leaving - never called')

    async def connect_clients(self):
        # Bot has a member start had to change name, not sure we are doign here to give good name...
        logger.info("fantasy bot connect clients enter")
        self.player_handler = PlayerHandler()
        self.fantasy_handler = FantasyHandler()
        await asyncio.gather(self.player_handler.start(), self.fantasy_handler.start())
        await self.fantasy_handler.init_listener(
            self.on_init_draft, self.on_new_draft, self.on_new_pick,
            self.on_init_users, self.on_update_users, self.player_handler
        )
        return 42

    def on_init_users(self, users):
        """Callback to initialize discord bot record of current external_users
        
        Not used atm!

        We get a list of users, objects of form: {
            'external_user_id': 'a9ba45b5-cbad-43f3-8dc9-b57188974007',
            'meta': {'discord_id': 143464912868474880},
            'name': 'ctpeepee#1273'
        }
        NB: in listener ignored some of the resp data to just give list of users
        """
        logger.info("fantasy bot on init users")
        # because using set here. if the database already has duplicated users could
        # get weird results where we get different version of user each time
        self.external_users = set(user['meta']['discord_id'] for user in users)
        logger.debug(f"fantasy bot on init users: {len(self.external_users)} users inited")

    def on_update_users(self, users):
        """Callback to update users

        Not using for now, will update set of users from join command
        """
        logger.info("fantasy bot on update users")

    def on_init_draft(self, drafts):
        """Callback to init draft interal state

        For when bot crashes/restarts. Set up internal state of drafts/picks so 
        that users can query when their next pick is scheduled, who the next
        pickers are, players left, etc

        We get a list of drafts: {
        'draft_id': 'eb824c78-164b-4973-bfac-b283f6e0705f',
        'league_id': 'b3c223bf-0409-4b54-88c7-bbb937c8111c',
        'meta': {},
        'period_id': '4b86d0e3-b6f6-482f-ae3f-5f6caa2afdc2',
        'team_drafts': [{
            'active_picks': [],
            'draft_choices': [],
            'external_user_id': '92de6fac-7df2-49ba-92d7-fff27f5b4d75',
            'fantasy_team_id': '5a4adfa5-2600-4236-9180-103f39435d90',
            'meta': {'discord_id': 143464912868474880},                   'name': 'ctpeepee#1273_team',
            'team_draft_id': '3dbc3d01-b11e-4a58-847a-30a191070523'
            }, ...]
        }
        """
        logger.info("fantasy bot on init draft")

    def on_new_draft(self, draft):
        logger.info("fantasy bot on new draft")

    def on_new_pick(self, pick):
        logger.info("fantasy bot on new draft")

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
        # TODO add which cog, module or whatever stuff is called form. atm just says "main"
        logger.info(f'{ctx.author.name} called {ctx.command.qualified_name} with {ctx.args[2:]}')

    async def on_command_completion(self, ctx):
        """An event that is called when a command has completed its invocation.

        This event is called only if the command succeeded, i.e. all checks have passed and the user input it correctly.
        """ 
        logger.info(f'{ctx.command.qualified_name} called by {ctx.author.name} completed')


bot = FantasyBot(command_prefix=COMMAND_PREFIX, case_insensitive=True,
    description=HELP_COMMAND_TEXT)

# pre connect to discord stuff
#asyncio.run(bot.connect_clients())

@bot.command()
async def reload(ctx):
    # TODO call on_ready stuff so cogs get events like they bot had just started?
    bot.reload_extension('fantasydota')
    bot.reload_extension('dev')

bot.load_extension('fantasydota')
bot.load_extension('dev')
bot.run(BOT_TOKEN)
