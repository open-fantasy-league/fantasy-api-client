import logging
import os

import dotenv
from discord.ext import commands

logging.basicConfig(level=logging.INFO)
dotenv.load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
COMMAND_PREFIX = '!'

if not BOT_TOKEN:
    print('No bot token found, check .env')
    exit()

bot = commands.Bot(command_prefix=COMMAND_PREFIX, case_insensitive=True,
    description="I am a penguin")

@bot.event
async def on_ready():
    print(f'{bot.user} has logged in!')

@bot.command()
async def hello(ctx):
    """Does this help?
    
    What if I need more help?
    """
    await ctx.send("Hello as a command!")

@bot.command()
async def rules(ctx):
    """List the rules"""
    the_rules = (
        "Rule 1: Follow rule 2\n"
        "Rule 2: See rule 1"
    )
    await ctx.send(the_rules)

@bot.group()
async def test(ctx):
    if ctx.invoked_subcommand is None:
        guild = ctx.guild.name
        user = ctx.author.name
        message = ctx.message.content
        await ctx.send(f'`{user}` said `{message}` in `{guild}`')

@test.command()
async def clean(ctx):
    """Clean channel of all messages"""
    await ctx.send("I am cleaning relax")

bot.run(BOT_TOKEN)

"""TODO
- delete all messages - https://stackoverflow.com/questions/43465082/python-discord-py-delete-all-messages-in-a-text-channel
- hot reload
- cogs
"""
