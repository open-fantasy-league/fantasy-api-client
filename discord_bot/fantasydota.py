"""
Fantasy Dota cog
"""
import asyncio

from discord.ext import commands

from messages.fantasy_msgs import DraftQueue
from utils.utils import simplified_str
from discord_bot.listener import PlayerHandler, FantasyHandler

import logging
logger = logging.getLogger(__name__)

# TODO @ThePianoDentist
RULES = '```lists how many players per team/per position```'
SCORING = '```ie 3 points assist, 4 points kill```'


class FantasyDota(commands.Cog):
    """An awesome fantasy dota 2 dota league"""
    def __init__(self, bot):
        self.bot = bot
        self.player_handler = None  # PlayerHandler()
        self.fantasy_handler = None  # FantasyHandler()

    async def start(self):
        logger.info("in start")
        self.player_handler = PlayerHandler()
        self.fantasy_handler = FantasyHandler()
        await asyncio.gather(self.player_handler.start(), self.fantasy_handler.start())
        return 42

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self.bot.user} has logged in!')
        await self.start()

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
        # TODO
        await ctx.send(f'{ctx.author.name} wants to join the league!')
    
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
    cant make this async, so it's a bit of a faff, doing async setup stuff
    :param bot:
    :return:
    """
    cog = FantasyDota(bot)

    # Cant start the clients here, because after setup...the bot creates its own event-loop,
    # and whichever used here is destroyed....which cancels the tasks for the clients that are listening to new msgs

    #cog.start()
    # IGNORE THE BELOW. APPARENTLY nowadays asyncio.run() just work (tm), and will create a new event loop for us,
    # to run that func, and then it switches back to the existing event-loop discord setup?

    #future = asyncio.run_coroutine_threadsafe(cog.start(), asyncio.get_event_loop())
    # future.result blocks the current thread....so that doesn't work.
    #     res = future.result()
    # Think do either need to just not wait for start to finish,
    # i.e. bot starts running whilst it's still starting up
    # could have commands check a self.initialized, that gets set at end of start, and error early if they hit it
    # (this would be a cool use of a decorator)

    # The alternative is to create a new thread to call `start` in, and we are able to then do future.result(),
    # which would wait in this thread, but the other thread would be able to do the work
    bot.add_cog(cog)

def teardown(bot):
    print('fantasydota teardown')