import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv


"""
main.py

Initialises and starts the bot.

py -3 ./src/main.py
"""


# Load cogs.
async def load():
    await bot.load_extension("bot")
    # await bot.load_extension("player")


load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="sudo", intents=intents, help_command=None,
                   activity=discord.Activity(type=discord.ActivityType.watching, name="shadowkingdom.org"))
                   
asyncio.run(load())
bot.run(os.getenv("TOKEN"))
