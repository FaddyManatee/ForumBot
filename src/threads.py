# https://discordpy.readthedocs.io/en/latest/index.html
import os
import re
import discord
import requests
import paginator
import botlog
import discord
from discord import app_commands
from discord.ext import commands, tasks
from dotenv import load_dotenv
from fetchrss import FetchRss, time_elapsed
from skbans import get_most_recent_punishment


load_dotenv()


class Threads(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        
        # If bot stops working, check if cookies in .env need updating first
        self.rss = FetchRss(os.getenv("COOKIE"))
        self.seperator = "---------------------------------\n"
        self.members = []
        self.new_embeds = []
        self.report_embeds = []
        self.appeal_embeds = []
        self.application_embeds = []


    async def generate_embeds(self, threads):
        embeds = []
        staff = []

        for thread in threads:
            embed = discord.Embed(title=thread["title"])
            
            avatar = thread["author_avatar"]

            # Use another image if the avatar is a default xenforo avatar.
            if "xenforo" in avatar:
                embed.set_author(name=thread["author"], url="https://shadowkingdom.org/members/{}.{}/".format(thread["author_formatted"],
                                 thread["author_id"]), 
                                 icon_url="https://i.postimg.cc/cJQnqTsS/unknown.jpg".format(thread["player"]))
            else:
                embed.set_author(name=thread["author"], url="https://shadowkingdom.org/members/{}.{}/".format(thread["author_formatted"],
                                 thread["author_id"]),
                                 icon_url=avatar)

            # Set the embed thumbnail to the thread author's player head.
            thumbnail = requests.get("https://minotar.net/helm/{}.png".format(thread["player"]))
            if thumbnail.status_code != 200:
                embed.set_thumbnail(url=os.getenv("UKN_IGN"))
            else:
                embed.set_thumbnail(url=thumbnail.url)


            embed.add_field(name="Player", value=discord.utils.escape_markdown(thread["player"]))

            # Different thread types display different embed fields.
            if thread["type"] == "server-appeal":
                embed.description = "Server punishment appeal\n[Click here to view]( {} )".format(thread["link"])
                embed.color = discord.Color.from_str("#ff2828")

                # Get the punished player's uuid to find their most recent punishment.
                uuid = requests.get("https://api.mojang.com/users/profiles/minecraft/{}".format(thread["player"])).json()["id"]
                punishment = get_most_recent_punishment(uuid, self.members)

                # Add the discord account of the moderator that made this punishment to staff ping list.
                staff.append(punishment["mod_discord"])

                embed.add_field(name="Staff member", value=discord.utils.escape_markdown(punishment["moderator"]))
                embed.add_field(name="Punishment", value=punishment["type"])
                embed.add_field(name="Reason", value=punishment["reason"], inline=False)

            elif thread["type"] == "discord-appeal":
                embed.description = "Discord punishment appeal\n[Click here to view]( {} )".format(thread["link"])
                embed.color = discord.Color.from_str("#ff2828")

            elif thread["type"] == "staff-app":
                embed.description = "Staff application\n[Click here to view]( {} )".format(thread["link"])
                embed.color = discord.Color.from_str("#00f343")

            elif "player-report" in thread["type"]:
                embed.description = "Player report\n[Click here to view]( {} )".format(thread["link"])
                embed.color = discord.Color.from_str("#19b5fe")

            embeds.append((embed, thread))
        
        return embeds, list(set(staff))


    @commands.Cog.listener()
    async def on_ready(self):
        print("Logged in as {0.user}".format(self.bot))
        self.members = [member for member in self.bot.get_all_members() if not member.bot]

        # Start task to periodically execute FetchRss.run()
        if self.fetcher.is_running() == False:
            self.fetcher.start()


    # Sync the bot's command tree globally. Executable by the bot owner only.
    @app_commands.command(name="sync", description="Bot owner only")
    async def sync(self, interaction: discord.Interaction):
        if interaction.user.id == int(os.getenv("OWNER_ID")):
            await interaction.response.defer(ephemeral=True)
            await self.bot.tree.sync()
            await interaction.followup.send("Command tree synced")
        else:
            await interaction.response.send_message("You must be the owner to use this command!", ephemeral=True)


    # Display changelog.md in an embed.
    @app_commands.command(name="changelog", description="Show ForumBot version changelog")
    async def changelog(self, interaction: discord.Interaction):
        embed = discord.Embed(color=discord.Colour.from_str("#1cb4fa"), title="ForumBot changelog")

        # Get changelog.md from parent directory of bot.py
        embed.description = open(os.path.join(os.path.dirname(__file__), os.path.join("..", "changelog.md"))).read()

        # Find latest version string and display in footer.
        embed.set_footer(text="Version {} by FaddyManatee".format(re.findall(r"\d\.\d\.\d", embed.description)[-1]),
                icon_url="https://i.postimg.cc/br0cHz36/Logo.png")
        await interaction.response.send_message(embed=embed)
            

    @app_commands.command(name="viewthreads", description="View important forum threads that still need to be closed")
    @app_commands.describe(type="Thread type")
    @app_commands.choices(type=[
        discord.app_commands.Choice(name="new", value=1),
        discord.app_commands.Choice(name="all", value=2),
        discord.app_commands.Choice(name="appeal", value=3),
        discord.app_commands.Choice(name="report", value=4),
        discord.app_commands.Choice(name="staffapp", value=5)
    ])
    async def viewThreads(self, interaction: discord.Interaction, type: discord.app_commands.Choice[int]):
        await botlog.command_used(interaction.user.name + "#" + interaction.user.discriminator,
                                interaction.command.name + " " + type.name)

        if type.name == "new":
            threads = self.new_embeds
        
        elif type.name == "all":
            threads = self.appeal_embeds + self.application_embeds

        elif type.name == "appeal":
            threads = self.appeal_embeds

        elif type.name == "report":
            threads = self.report_embeds

        elif type.name == "staffapp":
            threads = self.application_embeds
        
        # Build up a list of embed objects with their elapsed time since postal.
        embeds = []
        for embed in threads:
            embed[0].set_footer(text=time_elapsed(embed[1]))
            embeds.append(embed[0])

        # Create custom buttoms to override default paginator button appearance.
        if len(threads) > 0:
            next_button = discord.ui.Button(label="\u25ba", style=discord.ButtonStyle.primary)
            prev_button = discord.ui.Button(label="\u25c4", style=discord.ButtonStyle.primary)
            
            await paginator.Simple(NextButton=next_button, PreviousButton=prev_button, DeleteOnTimeout=True).start(interaction, embeds)
        else:
            await interaction.response.send_message("There are no open threads of type `{}` to display".format(type.name))


    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        
        # Triggered if forgor appears in the message.
        if "forgor" in message.content.lower():
            await message.add_reaction("\U0001f480")

        # Triggered on any occurrence of the word "ham".
        parsed = re.search(r"\s*ham($|[ .,!?\-'])", message.content.lower())
        if parsed is not None:
            await message.add_reaction("<:ham:1061984465548742656>")

        # Triggered on @here or @everyone with message text containing "meeting time".
        if  message.mention_everyone and "meeting time" in message.content.lower():
            await message.add_reaction("<:whygod:1061614468234235904>")
            return

        # Triggered on any occurrence of the substring "sus", or words "among us" or "amogus".
        parsed = re.search(r"sus|\s*(among us|amogus)($|[ .,!?\-'])",
                        message.content.lower())
        if parsed is not None:
            await message.channel.send("<:sus:1061610886365712464>")
            return

        # Triggered on any occurrence of the word "puzzle"
        parsed = re.search(r"\s*puzzle($|[ .,!?\-'])", message.content.lower())
        if parsed is not None:
            await message.reply(os.getenv("PUZZLE_GIF"))
            return

        # Triggered if message text is "hello?" exactly.
        if message.content.lower() == "hello?":
            await message.channel.send(":musical_note: Is it me you're looking for? :musical_note:")
            return

        # Triggered on any occurrence of the words "get c".
        parsed = re.search(r"\s*get c($|[ .,!?\-'])", message.content.lower())
        if parsed is not None:
            await message.reply(os.getenv("WHY_GIF"))
            return

        await self.bot.process_commands(message)


    @tasks.loop(minutes=30.0)
    async def fetcher(self):
        detected = self.rss.run()
        await botlog.new_threads(detected)

        if (detected > 0):
            channel = self.bot.get_channel(int(os.getenv("CHANNEL_ID")))
            threads = self.rss.get_new_threads()
            count = len([thread for thread in threads if thread["type"] == "staff-app"])

            self.new_embeds, _ = await self.generate_embeds(self.rss.get_new_threads())
            self.appeals = self.rss.get_appeal_threads()
            self.appeal_embeds, staff = await self.generate_embeds(self.appeals)

            self.application_embeds, _ = await self.generate_embeds(self.rss.get_application_threads())
            
            ping_staff = ""
            if len(staff) > 0:
                for member in staff:
                    if member is not None:
                        ping_staff += "<@{}>\n".format(member.id)

            embed = discord.Embed(color=discord.Colour.from_str("#1cb4fa"),
                            title=":incoming_envelope: ***You've got mail !***")

            embed.description = self.seperator + \
                                ":scales: {} new appeal(s)\n".format(len(threads) - count) + \
                                ":pencil: {} new application(s)\n".format(count) + \
                                self.seperator + \
                                ":bulb: Use `/viewthreads new`"
            
            if len(ping_staff) > 0:
                await channel.send(ping_staff, embed=embed)
            else:
                await channel.send(embed=embed)

            # Start running the open thread reminder task if not already running.
            if self.reminder.is_running() == False:
                self.reminder.start()


    @tasks.loop(hours=168)
    async def reminder(self):
        channel = self.bot.get_channel(int(os.getenv("CHANNEL_ID")))
        threads = self.rss.get_open_threads()

        # Send weekly open thread reminder embed. 
        if len(threads) > 0 and self.reminder.current_loop > 0:
            embed = discord.Embed(color=discord.Colour.from_str("#1cb4fa"),
                    title=":books: ***Threads need attention***")

            embed.description = self.seperator + ":thread: There are **{}** open thread(s)\n".format(len(threads)) + \
                                self.seperator + \
                                ":bulb: Use `/viewthreads all`"

            await channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Threads(bot))
