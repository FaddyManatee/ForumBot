# https://discordpy.readthedocs.io/en/latest/index.html
from operator import truediv
import os
import discord
import fetchrss as sk
from discord.ext import commands, tasks
from dotenv import load_dotenv


load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='$', intents=intents, help_command=None)

# If bot stops working, check if cookies in .env need updating first
rss = sk.FetchRss(os.getenv("COOKIES"))


@bot.event
async def on_ready():
    print('Logged in as {0.user}'.format(bot))
    members = [member for member in bot.get_all_members() if not member.bot]
    print(members[0].display_name)
    fetcher.start()


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content == "Do you read me?":
        await message.channel.send("Affirmative")

    await bot.process_commands(message)


@tasks.loop(minutes=10.0)
async def fetcher():
    detected = rss.run()

    if (detected > 0):
        channel = bot.get_channel(int(os.getenv("CHANNEL_ID")))
        await channel.send("New threads: {}".format(detected))


bot.run(os.getenv("TOKEN"))
