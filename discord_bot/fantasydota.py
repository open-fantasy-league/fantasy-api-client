"""
Fantasy Dota cog
"""
import logging
import uuid

from discord.ext import commands

from messages.fantasy_msgs import DraftQueue, ExternalUser, FantasyTeam
from utils.utils import simplified_str
from data.dota_ids import FANTASY_LEAGUE_ID # TODO real fantasy id


logger = logging.getLogger(__name__)

# TODO @ThePianoDentist
RULES = '```lists how many players per team/per position```'
SCORING = '```ie 3 points assist, 4 points kill```'


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
        # TODO Do we need to worry about the below warning?
        # Warning This function is not guaranteed to be the first event called.
        # Likewise, this function is not guaranteed to only be called once.
        # This library implements reconnection logic and thus will end up calling
        # this event whenever a RESUME request fails.
        logger.info("fantasy dota cog is ready to party")



    # show we allow the public commands to also be called form dms?

    # maybe group rules/scoring by eg info - `info scoring/rules`
    @commands.command()
    async def rules(self, ctx):
        """List the rules"""
        await ctx.send(RULES)

    @commands.command()
    async def scoring(self, ctx):
        """List the scoring system"""
        await ctx.send(SCORING)

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
        """Join the league!"""
        # TODO:
        # - check if already exist?
        # - get proper fantasy id from somewhere
        # - other error handling?
        # - move this stuff into listener? or summit
        username = f'{ctx.author.name}#{ctx.author.discriminator}' # do we want to use discriminator?
        user_id = ctx.author.id # should this be string?
        user = ExternalUser(uuid.uuid4(), username, meta={'discord_id': user_id})
        team = FantasyTeam(
            uuid.uuid4(), user.external_user_id, FANTASY_LEAGUE_ID,
            f'{username}_team', meta={'discord_id': user_id}
        ) # very pep 8...
        await self.fantasy_handler.client.send_insert_users([user])
        await self.fantasy_handler.client.send_insert_fantasy_teams([team])
        await ctx.send(f'Congratulations {ctx.author.name} you have succesfully joined the league!')
    
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
    async def pick(self, ctx, hero):
        """Make your pick"""
        # TODO
        await ctx.send(f'{ctx.author.name} picked {hero}')

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
                    f'Invalid player: {e}. !players to see available picks. '
                    f'I.e. order! puppey fng zai micke'
                )
            discord_id = ctx.author.id
            try:
                draft_queue = DraftQueue(self.fantasy_handler.discord_user_id_to_fantasy_id[discord_id], player_ids)
            except KeyError:
                # TOMAYBEDO could auto join league on any interaction like this.
                return await ctx.send(
                    'You are not currently registered to this league. Please type join! in main channel'
                )
            resp = await self.fantasy_handler.client.send_insert_draft_queues([draft_queue])
            if resp["mode"] == "resp":  # i.e. not mode: "error"
                await ctx.send(f'{ctx.author.name} has set their order as: {", ".join(args)}')
            else:
                print(resp)
                await ctx.send(f'Something went horribly wrong. Please DM a mod to investigate')
        else:
            await ctx.send(f'Provide a space separated list. I.e. Ex. order! puppey fng zai micke')

        async def on_new_draft(self, msg):
            print(msg)


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