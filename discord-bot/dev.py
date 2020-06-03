"""
Fantasy Dota cog
"""

from random import randint

from discord import Color, TextChannel, Role
from discord.ext import commands


class Dev(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


# ```@bot.group()
# async def group_name(ctx):
#     if ctx.invoked_subcommand is None: # avoid calling if using subcommand
#         # do stuff

# @group_name.command()
# async def sub_command_name(ctx):
#     #do stuff
# ```
    
    
    @commands.command()
    async def clear(self, ctx):
        """Clear up to 100 channel messages."""
        channel = ctx.message.channel
        await channel.purge()
        await ctx.send("Finished cleaning. Bery nice.")

    @commands.group()
    async def create(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Create what?")

    @create.command()
    async def channel(self, ctx, name):
        # @TODO private channel/permissions stuff
        new_channel = await ctx.guild.create_text_channel(name)
        if new_channel:
            await ctx.send(f'Created new channel - {new_channel.name}')
        else:
            await ctx.send(f'Failed')

    @create.command()
    async def role(self, ctx, name):
        random_color = Color.from_rgb(randint(0, 255), randint(0, 255), randint(0, 255))
        new_role = await ctx.guild.create_role(name=name, color=random_color)
        if new_role:
            await ctx.send(f'Created new role - {new_role.name}')
        else:
            await ctx.send(f'Failed')

    @commands.group()
    async def delete(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Delete what?")
    
    @delete.command()
    async def channel(self, ctx, *, channel: TextChannel):
        if channel:
            deleted_name = channel.name
            await channel.delete()
            await ctx.send(f'Channel {deleted_name} was deleted')
        else:
            await ctx.send(f'No channel found')

    @delete.command()
    async def role(self, ctx, *, role: Role):
        if role:
            deleted_name = role.name
            await role.delete()
            await ctx.send(f'Role {deleted_name} was deleted')
        else:
            await ctx.send(f'No channel found')



def setup(bot):
    bot.add_cog(Dev(bot))    

def teardown(bot):
    print('dev teardown')