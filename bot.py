# https://discordpy.readthedocs.io/en/latest/index.html
import os
import discord
import requests
import fetchrss as sk
from math import floor
from datetime import datetime as dt
from discord import app_commands
from discord.ext import commands, tasks
from dotenv import load_dotenv


load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="sudo ", intents=intents, help_command=None)

# If bot stops working, check if cookies in .env need updating first
rss = sk.FetchRss(os.getenv("COOKIE"), os.getenv("USER_AGENT"))


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


@tasks.loop(minutes=30.0)
async def fetcher():
    detected = rss.run()
    print(detected)

    if (detected > 0):
        channel = bot.get_channel(int(os.getenv("CHANNEL_ID")))
        threads = rss.getNewThreads()

        await channel.send("New threads: {}".format(len(threads)))
        
        for thread in threads:
            embed = discord.Embed(title=thread["title"])
            
            avatar = thread["author_avatar"]

            if "xenforo" in avatar:
                embed.set_author(name=thread["author"], url="https://shadowkingdom.org/members/{}.{}/".format(thread["author_formatted"], thread["author_id"]), icon_url="https://i.postimg.cc/cJQnqTsS/unknown.jpg".format(thread["player"]))
            else:
                embed.set_author(name=thread["author"], url="https://shadowkingdom.org/members/{}.{}/".format(thread["author_formatted"], thread["author_id"]), icon_url=avatar)


            thumbnail = requests.get("https://minotar.net/helm/{}.png".format(thread["player"]))


            if thumbnail.status_code != 200:
                embed.set_thumbnail(url="https://minotar.net/helm/{}.png".format(os.getenv("UNKNOWN_IGN")))
            else:
                embed.set_thumbnail(url=thumbnail.url)


            embed.add_field(name="Player", value=discord.utils.escape_markdown(thread["player"]))
            

            if thread["type"] == "server-appeal":
                embed.description = "Server punishment appeal"
                embed.color = discord.Color.from_str("#ff2828")
                embed.add_field(name="Staff member", value=thread["moderator"])

            elif thread["type"] == "discord-appeal":
                embed.color = discord.Color.from_str("#ff2828")
                embed.description = "Discord punishment appeal"

            elif thread["type"] == "staff-app":
                embed.color = discord.Color.from_str("#00f343")
                embed.description = "Staff application"

            embed.add_field(name="Link", value=thread["link"], inline=False)
            time_spanned = floor((dt.now() - thread["time"]).total_seconds() / 3600)


            if time_spanned >= 24:
                embed.set_footer(text=str(floor(time_spanned / 24)) + "d ago")
            else:
                embed.set_footer(text=str(time_spanned) + "h ago")

            await channel.send(embed=embed)


bot.run(os.getenv("TOKEN"))
