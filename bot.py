# https://discordpy.readthedocs.io/en/latest/index.html
import os
import discord
import fetchrss as sk
from discord import app_commands
from discord.ext import commands, tasks
from dotenv import load_dotenv


load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="sudo ", intents=intents, help_command=None)

# If bot stops working, check if cookies in .env need updating first
rss = sk.FetchRss(os.getenv("COOKIES"))


@bot.event
async def on_ready():
    print("Logged in as {0.user}".format(bot))
    members = [member for member in bot.get_all_members() if not member.bot]
    fetcher.start()


@bot.tree.command(name="sync", description="Bot owner only")
async def sync(interaction: discord.Interaction):
    if interaction.user.id == int(os.getenv("OWNER_ID")):
        await interaction.response.defer(ephemeral=True)
        await bot.tree.sync()
        await interaction.followup.send("Command tree synced")
    else:
        await interaction.response.send_message("You must be the owner to use this command!", ephemeral=True)


@bot.tree.command(name="viewthreads", description="View important forum threads")
@app_commands.describe(types="Thread type")
@app_commands.choices(types=[
    discord.app_commands.Choice(name="new", value=1),
    discord.app_commands.Choice(name="all", value=2),
    discord.app_commands.Choice(name="appeals", value=3),
    discord.app_commands.Choice(name="application", value=4),
])
async def newThreads(interaction: discord.Interaction, types: discord.app_commands.Choice[int]):
    if types.name == "new":
        threads = rss.getNewThreads()
    
    elif types.name == "all":
        threads = rss.getOpenThreads()

    elif types.name == "appeals":
        threads = rss.getServerThreads()
        threads.extend(rss.getDiscordThreads())

    elif types.name == "application":
        threads = rss.getApplicationThreads()
    
    await interaction.response.send_message("Test {}".format(types.name))


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content == "Do you read me?":
        await message.channel.send("Affirmative")

    await bot.process_commands(message)


@tasks.loop(minutes=5.0)
async def fetcher():
    detected = rss.run()
    print(detected)

    if (detected > 0):
        channel = bot.get_channel(int(os.getenv("CHANNEL_ID")))
        threads = rss.getNewThreads()
        await channel.send("New threads: {}".format(len(threads)))


bot.run(os.getenv("TOKEN"))
