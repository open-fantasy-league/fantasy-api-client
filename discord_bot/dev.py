"""
Dev cog
"""
import logging
from random import randint

from discord import Color, TextChannel, Role, Member, PermissionOverwrite
from discord.utils import get as dget # LUL
from discord.ext import commands


logger = logging.getLogger(__name__)

class Dev(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    async def clear(self, ctx):
        """Clear stuff"""
        if ctx.invoked_subcommand is None:
            await ctx.send("Clear what?")

    @clear.command(name="messages")
    async def clear_messages(self, ctx):
        """Clear up to 100 channel messages."""
        channel = ctx.message.channel
        await channel.purge()
        await ctx.send("Finished cleaning. Bery nice.")
    
    @clear.command(name="channels")
    async def clear_channels(self, ctx):
        """Delete all channels"""
        for channel in ctx.guild.channels:
            if channel.name not in ["ct-test", "jk-test", "Testing"]:
                await channel.delete()
        if ctx.channel in ctx.guild.channels: # even with this check we get 404 channel not foudn if called from channel we are deleting
            await ctx.send("Finished cleaning. Bery nice.")

    # TODO clear categroies?
    
    @clear.command(name="roles")
    async def clear_roles(self, ctx):
        """Delete all roles"""
        for role in ctx.guild.roles:
            if role.managed or role.is_default() or role.name in ["admin"]:
                continue
            await role.delete()
        await ctx.send("Finished cleaning. Bery nice.")
    
    @commands.group()
    async def create(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Create what?")

    @create.command(name="channel")
    async def create_channel(self, ctx, name, role: Role = None):
        overwrites = {}
        if role:
            overwrites = {
                ctx.guild.default_role: PermissionOverwrite(read_messages=False),
                role: PermissionOverwrite(read_messages=True)
            }
        new_channel = await ctx.guild.create_text_channel(name, overwrites=overwrites)
        await ctx.send(f'Created new channel - {new_channel.name}')

    @create.command()
    async def private_channel(self, ctx, name, *members):
        if len(members) == 0:
            await ctx.send("Please gimmie some members")
            return
        overwrites = {ctx.guild.default_role: PermissionOverwrite(read_messages=False)}
        for m in members: # who even likes comprehensions?
            member = dget(ctx.guild.members, name=m)
            if member:
                overwrites[member] = PermissionOverwrite(read_messages=True)
        if len(overwrites) == 0:
            await ctx.send("You didnt give me any valid members")
            return
        new_channel = await ctx.guild.create_text_channel(name, overwrites=overwrites)
        await ctx.send(f'Created new channel - {new_channel.name} some people who shall not be named because i cant be arse to implement it')

    @create.command(name="role")
    async def create_role(self, ctx, name):
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

    @delete.command(name="channel")
    async def delete_channel(self, ctx, *, channel: TextChannel):
        if channel:
            deleted_name = channel.name
            await channel.delete()
            await ctx.send(f'Channel {deleted_name} was deleted')
        else:
            await ctx.send(f'No channel found')

    @delete.command(name="role")
    async def delete_role(self, ctx, *, role: Role):
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

    @add.command(name="role")
    async def add_role(self, ctx, member: Member, role: Role):
        if member and role:
            await member.add_roles(role)
            await ctx.send(f'{member} added to {role}')
        else:
            await ctx.send('no workie')

    @commands.group()
    async def remove(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Remove what?")

    @remove.command(name="role")
    async def remove_role(self, ctx, member: Member, role: Role):
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
    
    @commands.command()
    async def info(self, ctx):
        await ctx.send((ctx.author.name, ctx.author.discriminator, ctx.author.id))

    # @commands.command()
    # async def echo(self, ctx, *, s):
    #     await ctx.send(s)



def setup(bot):
    logger.info("cog setup")
    bot.add_cog(Dev(bot))    

def teardown(bot):
    logger.info('cog teardown')