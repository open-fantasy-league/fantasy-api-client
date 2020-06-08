"""
Fantasy Dota cog
"""
import logging
import uuid
from pprint import pformat

from discord import PermissionOverwrite
from discord.ext import commands
from discord.utils import get as dget # This cant go wrong surely


from messages.fantasy_msgs import DraftQueue, ExternalUser, FantasyTeam, DraftPick
from utils.channel_text import SCORING_TEXT, HELP_TEXT, RULES_TEXT
from utils.errors import ApiException
from utils.utils import simplified_str
from data.dota_ids import FANTASY_LEAGUE_ID # TODO real fantasy id


logger = logging.getLogger(__name__)

# TODO @ThePianoDentist
CATEGORY_NAME = 'Fantasy Dota'
HELP_CHANNELS = {
    'Help': HELP_TEXT,
    'Rules': RULES_TEXT,
    'Scoring': SCORING_TEXT
}
PRIVATE_CHANNELS = ['Leaderboard', 'Pro Leaderboard']
PUBLIC_CHANNELS = ['Chat']


class FantasyDota(commands.Cog):
    """An awesome fantasy dota 2 dota league"""
    def __init__(self, bot):
        self.bot = bot

    @property
    def fantasy_handler(self):
        return self.bot.fantasy_handler

    @property
    def player_handler(self):
        return self.bot.player_handler

    # Listeners

    @commands.Cog.listener()
    async def on_member_join(self, member):
        # TODO welcome member suggest they join bla bla
        pass
        # channel = member.guild.system_channel
        # if channel is not None:
        #     await channel.send('Welcome {0.mention}.'.format(member))

    @commands.Cog.listener()
    async def on_ready(self):
        """Initial discord related set up 

        TODO:
        - Do we need to worry about the below warning?
            Warning This function is not guaranteed to be the first event called.
            Likewise, this function is not guaranteed to only be called once.
            This library implements reconnection logic and thus will end up calling
            this event whenever a RESUME request fails.
        """
        logger.info("Cog: On Ready enter")
        for guild in self.bot.guilds:
            # TODO create method for this
            logger.info(f"Cog: Checking required channels for {guild.name}")
            category = dget(guild.categories, name=CATEGORY_NAME)
            if category:
                logger.info(f"Cog: Help category found")
                # For now just assume if catgeory is there we're done
            else:
                logger.info(f'Cog: Category not found - creating')
                # TODO force category at top?
                overwrites = {
                    guild.default_role: PermissionOverwrite(send_messages=False),
                }
                new_category = await guild.create_category(CATEGORY_NAME, overwrites=overwrites)
                logger.info(f'Cog: New category created - adding and populating channels')
                for name in HELP_CHANNELS:
                    new_channel = await guild.create_text_channel(name, category=new_category,
                                                                  overwrites=overwrites)
                    await new_channel.send(HELP_CHANNELS[name])
                logger.info(f'Cog: All help channels added and populated succsfully')
                for name in PRIVATE_CHANNELS:
                    await guild.create_text_channel(name, category=new_category)
                overwrites = {
                    guild.default_role: PermissionOverwrite(send_messages=True),
                }
                for name in PUBLIC_CHANNELS:
                    await guild.create_text_channel(name, category=new_category,
                                                    overwrites=overwrites)
                logger.info(f"Cog: All other channels created")
        logger.info("Cog On Ready leave")

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        """Handle joining a guild

        Does nothing atm but will want to run the same kind of create channels init
        set up we run on all guilds in on ready probs
        """
        

    # TODO show we allow the public commands to also be called form dms?
    # TODO maybe group rules/scoring by eg info - `info scoring/rules`
    # TODO if get fancy, make a custom check for whether the rules/scoring/help
    # commands are useable. for now only owner can use
    @commands.command()
    @commands.is_owner()
    async def rules(self, ctx):
        """List the rules"""
        await ctx.send(RULES_TEXT)

    @commands.command()
    @commands.is_owner()
    async def scoring(self, ctx):
        """List the scoring system"""
        await ctx.send(SCORING_TEXT)

    @commands.group()
    async def show(self, ctx):
        """Display various information"""
        if ctx.invoked_subcommand is None:
            await ctx.send("What would you like to show?")
    
    @show.command()
    async def leaderboard(self, ctx):
        """Display current leaderboard"""
        # TODO
        await ctx.send("Nice leaderboard you got here")

    @show.command()
    async def team(self, ctx):
        """Display your team"""
        # TODO
        await ctx.send(f'{ctx.author.name} wants to see their team right about now')

    @commands.command()
    async def join(self, ctx):
        """Join the league!
        
        TODO:
        - get proper fantasy id from somewhere
        - other error handling?
        - move this stuff into listener? or somewhere more sensible
        @IMPROVE
        - better api call to check user exists rather than keeping state
        """
        new_username = f'{ctx.author.name}#{ctx.author.discriminator}'  # do we want to use discriminator?
        new_user_id = ctx.author.id  # should this be string? (doesnt matter what type)
        if new_user_id in self.fantasy_handler.discord_user_id_to_fantasy_id:
            logger.warning(f'existing user {ctx.author.name} tried to join league')
            await ctx.send(f"Hey {ctx.author.name}, you're already in this league. Ya chump")
            return

        user = ExternalUser(uuid.uuid4(), new_username, meta={'discord_id': new_user_id})
        team = FantasyTeam(
            uuid.uuid4(), user.external_user_id, FANTASY_LEAGUE_ID,
            f'{new_username}', meta={'discord_id': new_user_id}
        ) 
        await self.fantasy_handler.add_user(ctx, user, team, new_user_id)

    @commands.command()
    async def players(self, ctx):
        """Print out players to pick from
        """
        players = self.player_handler.players
        printy = ""
        for team in self.player_handler.teams_and_players:
            print(team)
            printy += f'"{team["names"][0]["name"]}":  {", ".join(p["player"]["names"][0]["name"] for p in team["players"])}\n\n'
        await ctx.send(printy)

    @commands.group()
    async def draft(self, ctx):
        """Commands to use while in a draft"""
        if ctx.invoked_subcommand is None:
            # just print the info
            await self.info(ctx)
    
    @draft.command()
    async def info(self, ctx):
        """What info do I show?"""
        # TODO show next drafters, and when user up next.
        await ctx.send(f"next drafters bla bla\n {ctx.author.name} you pick in 2 seconds")

    @draft.command()
    @commands.guild_only() # TODO make usable in draft channel. maybe make only visible their too?
    async def pick(self, ctx, player):
        """Make your pick"""
        # TODO
        try:
            player_id = self.player_handler.simplified_player_names_to_id[simplified_str(player)]
        except KeyError:
            return await ctx.send(f'Invalid pick {player}. `!players ` to see available picks')
        fantasy_team_id = self.fantasy_handler.get_user_team(ctx.author.id).fantasy_team_id
        draft_id = None
        await self.fantasy_handler.client.send_insert_draft_pick(DraftPick(player_id, fantasy_team_id, draft_id))
        await ctx.send(f'{ctx.author.name} picked {player}')

    @draft.command()
    @commands.dm_only()
    async def order(self, ctx, *args):
        """Set your draft queue order for automatic picks"""
        # Can do this if there is a particular reason for wanting csv
        # order(self, ctx, *, heros) will return heros as whatever is typed
        # after "order"
        # I now think space-separated is fine (was imaging sometimes pros had spaces in their names, but
        # a) they actually dont when checking wiki. b) even if they do can just say "dont use spaces")
        if len(args) > 0:
            player_names = args
            try:
                player_ids = [self.player_handler.simplified_player_names_to_id[simplified_str(n)] for n in player_names]
            except KeyError as e:
                # TOMAYBEDO return full player-typed name, not simplified.
                return await ctx.send(
                    f'Invalid player: {e}. `!players` to see available picks. '
                    f'I.e. `!draft order puppey fng zai micke`'
                )
            discord_id = ctx.author.id
            try:
                draft_queue = DraftQueue(self.fantasy_handler.get_user_team(discord_id).fantasy_team_id, player_ids)
            except KeyError:
                # TOMAYBEDO could auto join league on any interaction like this.
                return await ctx.send(
                    'You are not currently registered to this league. Please type join! in main channel'
                )
            try:
                await self.fantasy_handler.client.send_insert_draft_queues([draft_queue])
                return await ctx.send(f'Success!')
            except ApiException:
                await ctx.send(f'Something went horribly wrong. Please DM a mod to investigate')
        else:
            await ctx.send(f'Provide a space separated list. I.e. Ex. order! puppey fng zai micke')


def setup(bot):
    """
    :param bot:
    :return:
    """
    logger.info('cog setup')
    cog = FantasyDota(bot)
    bot.add_cog(cog)

def teardown(bot):
    logger.info('cog teardown')