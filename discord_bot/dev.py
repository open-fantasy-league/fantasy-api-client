"""
Fantasy Dota cog
"""

from random import randint

from discord import Color, TextChannel, Role, Member, PermissionOverwrite
from discord.ext import commands


class Dev(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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
    async def channel(ctx, name, role: Role = None):
        # @TODO private channel/permissions stuff
        overwrites = {}
        if role:
            overwrites = {
                ctx.guild.default_role: PermissionOverwrite(read_messages=False),
                role: PermissionOverwrite(read_messages=True)
            }
        new_channel = await ctx.guild.create_text_channel(name, overwrites=overwrites)
        await ctx.send(f'Created new channel - {new_channel.name}')

    @create.command()
    async def role(ctx, name):
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
    
    # what the actual fuck is going on. why do group commands sometimes need self
    # sometimes dont...

    @delete.command()
    async def channel(self, ctx, *, channel: TextChannel):
        if channel:
            deleted_name = channel.name
            await channel.delete()
            await ctx.send(f'Channel {deleted_name} was deleted')
        else:
            await ctx.send(f'No channel found')

    @delete.command()
    async def role(ctx, *, role: Role):
        if role:
            deleted_name = role.name
            await role.delete()
            await ctx.send(f'Role {deleted_name} was deleted')
        else:
            await ctx.send(f'No channel found')

    @commands.group()
    async def add(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Add what?")

    @add.command()
    async def role(self, ctx, member: Member, role: Role):
        if member and role:
            await member.add_roles(role)
            await ctx.send(f'{member} added to {role}')
        else:
            await ctx.send('no workie')

    @commands.group()
    async def remove(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Remove what?")

    @remove.command()
    async def role(self, ctx, member: Member, role: Role):
        if member and role:
            await member.remove_roles(role)
            await ctx.send(f'{member} removed from {role}')
        else:
            await ctx.send('no workie')
    
    @commands.command()
    async def pm(self, ctx, member: Member, *, message):
        if member:
            await member.send(message)
            await ctx.send(f'Private message sent to {member.name}')


def setup(bot):
    print("in dev setup")
    bot.add_cog(Dev(bot))    

def teardown(bot):
    print('dev teardown')