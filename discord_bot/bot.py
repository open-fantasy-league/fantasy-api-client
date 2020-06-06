import logging
import os

import dotenv
from discord.ext import commands

logging.basicConfig(level=logging.DEBUG)
dotenv.load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
COMMAND_PREFIX = '!'
# TODO @ThePianoDentist
HELP = 'who to contact for more info,\n a sort of faq'

if not BOT_TOKEN:
    print('No bot token found, check .env')
    exit()


bot = commands.Bot(command_prefix=COMMAND_PREFIX, case_insensitive=True,
    description=HELP)

@bot.command()
async def reload(ctx):
    bot.reload_extension('fantasydota')
    bot.reload_extension('dev')

bot.load_extension('fantasydota')
bot.load_extension('dev')
bot.run(BOT_TOKEN)
