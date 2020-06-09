import asyncio
import logging
import os
from collections import namedtuple
from pprint import pformat

import dotenv
from discord import PermissionOverwrite
from discord.ext import commands
from discord.utils import get as dget # This cant go wrong surely

from data.dota_ids import FANTASY_PLAYER_LEADERBOARD_ID, FANTASY_LEAGUE_ID, FANTASY_USER_LEADERBOARD_ID
from discord_bot.listener import PlayerHandler, FantasyHandler, LeaderboardHandler
from discord_bot.fantasydota import CATEGORY_NAME  # This is bad and will hurt us at some point
from messages.fantasy_msgs import DraftUpdate
from utils.channel_text import HELP_COMMAND_TEXT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

dotenv.load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
# TODO league_id <-> guild_id
GUILD_ID = int(os.getenv('GUILD_ID'))  # will fail if not set 

DEV = True if os.getenv('DEV') else False
COMMAND_PREFIX = '!'

if not BOT_TOKEN:
    print('No bot token found, check .env')
    exit()


class FantasyBot(commands.Bot):

    def __init__(self, *args, **kwargs):
        # handlers
        self.player_handler = None
        self.fantasy_handler = None
        self.leaderboard_handler = None

        # Internal state
        # Be careful users is a member of Bot
        self.external_users = None  # not used atm
        super().__init__(*args, **kwargs)

    async def on_ready(self):
        logger.info(f'fantasy bot on ready entered')
        # TOMAYBEDO now that connect clients also sets up listeners think we need to 
        # do something to prevent user commands while bot is setting up
        await self.connect_clients()
        logger.info(f'fantasy bot on ready leaving')

    async def connect_clients(self):
        # Bot has a member start had to change name, not sure we are doign here to give good name...
        logger.info("FantasyBot: connect clients enter")
        self.player_handler = PlayerHandler()
        self.fantasy_handler = FantasyHandler()
        self.leaderboard_handler = LeaderboardHandler()
        logger.info("FantasyBot:ConnectClients: starting handlers")
        await asyncio.gather(self.player_handler.start(), self.fantasy_handler.start(),
                             self.leaderboard_handler.start())
        logger.info("FantasyBot:ConnectClients: init fantasy listener")
        asyncio.create_task(self.fantasy_handler.init_listener(
            self.on_init_draft, self.on_new_draft, self.on_new_pick,
            self.on_init_users, self.on_update_users, self.player_handler
        ))

        logger.info("FantasyBot:ConnectClients: init leaderboard listener")
        asyncio.create_task(self.leaderboard_handler.init_listener(self.on_init_leaderboards,
                                                     self.on_update_leaderboards))
        logger.info("FantasyBot: connect clients exit")

    async def on_init_leaderboards(self, leaderboards):
        """Init our leaderboards

        This should probably be in fantasydota cog seeing as that is where
        discordy stuff like printing output is supposed to happen. It's
        also where the leaderboard channels are created.
        
        OH YEAH... thought could have this here for now but channels wont even be
        made yet...
        """
        logger.info("FantasyBot: on init leaderboards enter")
        # for guild in self.guilds: # TODO
        guild = self.get_guild(GUILD_ID)
        new_leaderboard = new_pro_leaderboard = None
        for leaderboard in leaderboards:
            if leaderboard["league_id"] == FANTASY_LEAGUE_ID:
                if leaderboard["leaderboard_id"] == FANTASY_USER_LEADERBOARD_ID:
                    new_leaderboard = leaderboard
                elif leaderboard["leaderboard_id"] == FANTASY_PLAYER_LEADERBOARD_ID:
                    new_pro_leaderboard = leaderboard
        if new_leaderboard is None or new_pro_leaderboard is None:
            logger.error(f'FantasyBot:on_init_leaderboards: failed to find leaderboards')
            return
        leaderboard_channel = dget(guild.channels, name="leaderboard")
        pro_leaderboard_channel = dget(guild.channels, name="pro-leaderboard")
        if leaderboard_channel is None or pro_leaderboard_channel is None:
            logger.error('FantasyBot:on_init_leaderboards: failed to find leaderboard channels')
            return
        await leaderboard_channel.send(new_leaderboard["name"])
        await pro_leaderboard_channel.send(new_pro_leaderboard["name"])

    def on_update_leaderboards(self, leaderboards):
        logger.info("FantasyBot: on update leaderboards enter")

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

    async def on_new_draft(self, drafts):
        """Create channels for drafts and add correct users

        if need to keep track of discord channel id -> draft id use 
        send_update_drafts when know the channel ids. 
        """
        logger.info("FantasyBot: on new draft")
        # for guild in self.guilds: # TODO
        guild = self.get_guild(GUILD_ID)
        if guild is None:
            logger.error(f'FantasyBot:on_new_draft: cant find guild with id {GUILD_ID}')
            return
        for draft in drafts:
            logger.info(f'FantasyBot:on_new_draft: handling draft {draft["draft_id"]}')
            if draft['league_id'] != FANTASY_LEAGUE_ID:
                logger.error(f'FantasyBot:on_new_draft: unexpected league id {draft["league_id"]}')
                return
            overwrites = {guild.default_role: PermissionOverwrite(read_messages=False)}
            for team_draft in draft["team_drafts"]:
                member = guild.get_member(team_draft["meta"]["discord_id"])
                if member is None:
                    logger.error(f'FantasyBot:on_new_draft: failed to find member')
                    # return
                    continue
                overwrites[member] = PermissionOverwrite(read_messages=True)
            category = dget(guild.categories, name=CATEGORY_NAME)
            if category is None:
                logger.error("FantasyBot:on_new_draft: failed to find catgeory")
                return
            logger.info(f'FantasyBot:on_new_draft: creating new channel for draft {draft["draft_id"]}')
            # TODO CT should go into the fantasydota category (or a drafts subcategory)
            new_channel = await guild.create_text_channel(f'draft {draft["draft_id"]}', overwrites=overwrites,
                                                          category=category)
            self.fantasy_handler.draft_ids_to_channel_ids[draft["draft_id"]] = new_channel.id
            self.fantasy_handler.channel_ids_to_draft_ids[new_channel.id] = draft["draft_id"]
            await self.fantasy_handler.client.send_update_drafts([DraftUpdate(draft["draft_id"], meta={'channel_id': new_channel.id})])
            await new_channel.send(f'Welcome drafters!')
            await new_channel.send(self.fantasy_handler.future_draft_choices(draft["draft_id"]))

    async def on_new_pick(self, pick):
        logger.info("FantasyBot:on_new_pick: enter")
        user, draft_id, playername = pick
        guild = self.get_guild(GUILD_ID)
        if guild is None:
            logger.error(f'FantasyBot:on_new_pick: cant find guild with id {GUILD_ID}')
            return
        member = guild.get_member(user.meta["discord_id"])
        if member is None and DEV:
            Dummy = namedtuple("Dummy", "name")
            member = Dummy("tpain0")
        channel = guild.get_channel(self.fantasy_handler.draft_ids_to_channel_ids[draft_id])
        if member is None or channel is None:
            logger.error("FantasyBot:on_new_pick: failed to find member or draft channel")
            return
        # logger.error('\n')
        # logger.error(user.meta)
        # logger.error(str(channel))
        # logger.error(str(member))
        # logger.error(f'{member.name} just picked {playername}')
        # logger.error('\n')
        self.fantasy_handler.draft_choices[draft_id].popleft()
        await channel.send(f'**{member.name}** just picked **{playername}**')
        out = self.fantasy_handler.future_draft_choices(draft_id, limit=1, and_time=True)
        if out:
            await channel.send(out)
        else:
            await channel.send("Draft finished")

    async def on_command_error(self, ctx, error):
        """An error handler that is called when an error is raised inside a command either through user input error, check failure, or an error in your own code.

        A default one is provided (Bot.on_command_error())
        """
        # TOMAYBEDO print out something useful to users if command fails
        if DEV:
            await ctx.send(f'Input error: {error}')  
        await super().on_command_error(ctx, error)

    async def on_command(self, ctx):
        """An event that is called when a command is found and is about to be invoked.

        This event is called regardless of whether the command itself succeeds via error or completes.
        """
        # TODO add which cog, module or whatever stuff is called form. atm just says "main"
        channel_str = "private message" if ctx.guild is None else f'channel: {ctx.channel.name}'
        logger.info(f'{ctx.author.name} called {ctx.command.qualified_name} with {ctx.args[2:]} from {channel_str}')

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
@commands.has_role('admin')
async def reload(ctx):
    # TODO call on_ready stuff so cogs get events like they bot had just started?
    # This would mean could get init_listener stuff out of bot and into fantasy
    bot.reload_extension('fantasydota')
    if DEV:
        bot.reload_extension('dev')

bot.load_extension('fantasydota')
if DEV:
    bot.load_extension('dev')
bot.run(BOT_TOKEN)
