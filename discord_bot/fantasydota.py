"""
Fantasy Dota cog
"""

from discord.ext import commands

from messages.fantasy_msgs import DraftQueue
from utils.utils import simplified_str
from discord_bot.listener import PlayerHandler, FantasyHandler

# TODO @ThePianoDentist
RULES = '```lists how many players per team/per position```'
SCORING = '```ie 3 points assist, 4 points kill```'


class FantasyDota(commands.Cog):
    """An awesome fantasy dota 2 dota league"""
    def __init__(self, bot):
        self.bot = bot
        self.player_handler = PlayerHandler()
        self.fantasy_handler = FantasyHandler()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self.bot.user} has logged in!')

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
        # "think comma separated list of player names is good" - ThePianoDentist
        # Can do this if there is a particular reason for wanting csv
        # order(self, ctx, *, heros) will return heros as whatever is typed
        # after "order"
        if len(args) > 0:
            player_names = ["puppey", "derek", "fng"]
            try:
                player_ids = [self.player_handler.simplified_player_names_to_id[simplified_str(n)] for n in player_names]
            except KeyError as e:
                # TOMAYBEDO return full player-typed name, not simplified.
                return await ctx.send(
                    f'Invalid player: {e}. !players to see available picks. '
                    f'I.e. order! puppey, fng, zai, micke'
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
            await ctx.send(f'Provide a comma separated list. I.e. Ex. order! puppey, fng, zai, micke')

def setup(bot):
    bot.add_cog(FantasyDota(bot))    

def teardown(bot):
    print('fantasydota teardown')