# https://discordpy.readthedocs.io/en/latest/index.html
# https://pypi.org/project/rss-parser/

import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from rss_parser import Parser
from requests import get

load_dotenv()
xml = get("https://shadowkingdom.org/forums/ban-mute-appeals.15.rss")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='$', intents=intents, help_command=None)

@bot.event
async def on_ready():
    print('Logged in as {0.user}'.format(bot))

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content == "Do you read me?":
        await message.channel.send("Affirmative")

    print(message.content)
    await bot.process_commands(message)

bot.run(os.getenv("TOKEN"))
