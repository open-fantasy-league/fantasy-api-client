"""
Fantasy Dota cog
"""

from discord.ext import commands


class FantasyDota(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self.bot.user} has logged in!')

    @commands.command()
    async def hello(self, ctx):
        """Does this help?
        
        What if I need more help?
        """
        await ctx.send("Hello as a command!")

    @commands.command()
    async def rules(self, ctx):
        """List the rules"""
        the_rules = (
            "Rule 1: Follow rule 2\n"
            "Rule 2: See rule 1\n"
            "Rule 3: Too many rules\n"
            "Rule 4: Another stinking rule"
        )
        await ctx.send(the_rules)

    @commands.command()
    async def clear(self, ctx):
        """`Clear n` channel messages."""
        channel = ctx.message.channel
        await channel.purge()
        await ctx.send("Finished cleaning. Bery nice.")



def setup(bot):
    bot.add_cog(FantasyDota(bot))    

def teardown(bot):
    print('ext teardown')