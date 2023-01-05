# https://discordpy.readthedocs.io/en/latest/index.html
import os
import discord
import requests
import paginator
import botlog
from fetchrss import FetchRss
from skbans import get_most_recent_punishment
from difflib import get_close_matches
from math import floor
from datetime import datetime as dt
from discord import app_commands
from discord.ext import commands, tasks
from dotenv import load_dotenv


load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="sudo ", intents=intents, help_command=None,
                   activity=discord.Activity(type=discord.ActivityType.watching, name="shadowkingdom.org"))

# If bot stops working, check if cookies in .env need updating first
rss = FetchRss(os.getenv("COOKIE"))
members = []
new_embeds = []
appeal_embeds = []
application_embeds = []


async def generate_embeds(threads):
    embeds = []

    for thread in threads:
        embed = discord.Embed(title=thread["title"])
        
        avatar = thread["author_avatar"]

        if "xenforo" in avatar:
            embed.set_author(name=thread["author"], url="https://shadowkingdom.org/members/{}.{}/".format(thread["author_formatted"], thread["author_id"]), icon_url="https://i.postimg.cc/cJQnqTsS/unknown.jpg".format(thread["player"]))
        else:
            embed.set_author(name=thread["author"], url="https://shadowkingdom.org/members/{}.{}/".format(thread["author_formatted"], thread["author_id"]), icon_url=avatar)


        thumbnail = requests.get("https://minotar.net/helm/{}.png".format(thread["player"]))


        if thumbnail.status_code != 200:
            embed.set_thumbnail(url="https://minotar.net/helm/vvvvvvvvvvvv.png")
        else:
            embed.set_thumbnail(url=thumbnail.url)


        embed.add_field(name="Player", value=discord.utils.escape_markdown(thread["player"]))


        if thread["type"] == "server-appeal":
            embed.description = "Server punishment appeal\n[Click here to view]( {} )".format(thread["link"])
            embed.color = discord.Color.from_str("#ff2828")

            uuid = requests.get("https://api.mojang.com/users/profiles/minecraft/{}".format(thread["player"])).json()["id"]
            punishment = get_most_recent_punishment(uuid)
            embed.add_field(name="Staff member", value=punishment["moderator"])
            embed.add_field(name="Punishment", value=punishment["type"])
            embed.add_field(name="Reason", value=punishment["reason"], inline=False)

        elif thread["type"] == "discord-appeal":
            embed.description = "Discord punishment appeal\n[Click here to view]( {} )".format(thread["link"])
            embed.color = discord.Color.from_str("#ff2828")

        elif thread["type"] == "staff-app":
            embed.description = "Staff application\n[Click here to view]( {} )".format(thread["link"])
            embed.color = discord.Color.from_str("#00f343")


        time_spanned = (dt.now() - thread["time"]).total_seconds() / 3600


        if time_spanned >= 24:
            embed.set_footer(text=str(floor(time_spanned / 24)) + " days ago")
        
        elif time_spanned < 1:
            embed.set_footer(text=str(floor(time_spanned * 60)) + " minutes ago")

        else:
            embed.set_footer(text=str(round(time_spanned, 1)) + " hours ago")

        embeds.append(embed)
    
    return embeds


@bot.event
async def on_ready():
    print("Logged in as {0.user}".format(bot))
    global members
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


@bot.tree.command(name="viewthreads", description="View important forum threads that still need to be closed")
@app_commands.describe(type="Thread type")
@app_commands.choices(type=[
    discord.app_commands.Choice(name="new", value=1),
    discord.app_commands.Choice(name="all", value=2),
    discord.app_commands.Choice(name="appeals", value=3),
    discord.app_commands.Choice(name="application", value=4)
])
async def viewThreads(interaction: discord.Interaction, type: discord.app_commands.Choice[int]):
    await botlog.command_used(interaction.user.name + "#" + interaction.user.discriminator,
                              interaction.command.name + " " + type.name)

    if type.name == "new":
        threads = new_embeds
    
    elif type.name == "all":
        threads = appeal_embeds + application_embeds

    elif type.name == "appeals":
        threads = appeal_embeds

    elif type.name == "application":
        threads = application_embeds

    if len(threads) > 0:
        next_button = discord.ui.Button(label="\u25ba", style=discord.ButtonStyle.primary)
        prev_button = discord.ui.Button(label="\u25c4", style=discord.ButtonStyle.primary)
        
        await paginator.Simple(NextButton=next_button, PreviousButton=prev_button, DeleteOnTimeout=True).start(interaction, threads)
    else:
        await interaction.response.send_message("There are no open threads of type `{}` to display".format(type.name))


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
    await botlog.new_threads(detected)

    if (detected > 0):
        channel = bot.get_channel(int(os.getenv("CHANNEL_ID")))
        threads = rss.get_new_threads()
        count = len([thread for thread in threads if thread["type"] == "staff-app"])

        global new_embeds, appeal_embeds, application_embeds
        new_embeds = await generate_embeds(rss.get_new_threads())

        appeals = rss.get_server_threads()
        appeals.extend(rss.get_discord_threads())
        appeal_embeds = await generate_embeds(appeals)

        application_embeds = await generate_embeds(rss.get_application_threads())
        
        staff = []

        seperator = "-------------------------------------\n"
        ping_staff = ""
        if len(staff) > 0:
            ping_staff = "The following staff have a new appeal to respond to:\n"
            for member in staff:
                ping_staff += "<@{}>\n".format(member.id)

            if len(ping_staff) > 0:
                ping_staff + seperator

        await channel.send(":incoming_envelope: ***You've got mail !***\n" +
                        seperator + ping_staff +
                        ":scales: {} new appeals\n".format(len(threads) - count) +
                        ":pencil: {} new applications\n".format(count) +
                        seperator +
                        ":bulb: Use `/viewthreads new` to see them")


bot.run(os.getenv("TOKEN"))
