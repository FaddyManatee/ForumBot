from discord import app_commands
from discord.ext import commands, tasks
from dotenv import load_dotenv
from paginator import Paginator
from skscraper import Scraper
from skforum import *
import os
import re
import discord
import botlog
import discord

load_dotenv()


async def setup(bot: commands.Bot):
    await bot.add_cog(Bot(bot))


class Bot(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot        
        self.scraper = Scraper(os.getenv("COOKIE"))
        self.seperator = "---------------------------------\n"
        self.members = []
        self.new_embeds = []
        self.report_embeds = []
        self.appeal_embeds = []
        self.application_embeds = []


    async def generate_embeds(self, threads: list[Thread]) -> list[tuple[discord.Embed, discord.Member]]:
        embeds = []

        for thread in threads:
            if isinstance(thread, Appeal):
                embeds.append(thread.to_embed(self.members))
            else:
                embeds.append(thread.to_embed())
        
        # Return the list of tuples with embed and staff member to ping.
        return embeds


    @commands.Cog.listener()
    async def on_ready(self):
        print("Logged in as {0.user}".format(self.bot))
        # Get all non-bot members.
        self.members = [member for member in self.bot.get_all_members() if not member.bot]

        # Start task to periodically execute Scraper.run()
        if not self.scraper_task.is_running():
            self.scraper_task.start()


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
        await botlog.command_used(interaction.user.name + "#" + interaction.user.discriminator,
                                  interaction.command.name)
        
        embed = discord.Embed(color=discord.Colour.from_str("#1cb4fa"), title="ForumBot changelog")

        # Get changelog.md from parent directory of this file.
        embed.description = open(os.path.join(os.path.dirname(__file__), os.path.join("..", "changelog.md"))).read()

        # Find latest version string and display in footer.
        embed.set_footer(text="Version {} by FaddyManatee".format(re.findall(r"\d\.\d\.\d", embed.description)[-1]),
                icon_url="https://i.postimg.cc/br0cHz36/Logo.png")
        await interaction.response.send_message(embed=embed)
            

    @app_commands.command(name="viewthreads", description="View important forum threads that still need to be closed")
    @app_commands.describe(type="Thread type")
    @app_commands.choices(type=[
        discord.app_commands.Choice(name="new",      value=1),
        discord.app_commands.Choice(name="all",      value=2),
        discord.app_commands.Choice(name="appeal",   value=3),
        discord.app_commands.Choice(name="report",   value=4),
        discord.app_commands.Choice(name="staffapp", value=5)
    ])
    async def viewThreads(self, interaction: discord.Interaction, type: discord.app_commands.Choice[int]):
        await botlog.command_used(interaction.user.name + "#" + interaction.user.discriminator,
                                  interaction.command.name + " " + type.name)

        threads = []
        match type.value:
            case 1:
                threads = self.new_embeds
            case 2:
                threads = self.appeal_embeds + self.application_embeds
            case 3:
                threads = self.appeal_embeds
            case 4:
                threads = self.report_embeds
            case 5:
                threads = self.application_embeds
        
        try:
            # Build up a list of embed objects.
            embeds = []
            for item in threads:
                embeds.append(item[0])

            # Create custom buttoms to override default paginator button appearance.
            next_button = discord.ui.Button(label="\u25ba", style=discord.ButtonStyle.primary)
            prev_button = discord.ui.Button(label="\u25c4", style=discord.ButtonStyle.primary)
            
            await Paginator(next_button=next_button, previous_button=prev_button, 
                            delete_on_timeout=True).start(interaction, embeds)
        except ValueError:
            await interaction.response.send_message("There are no open threads of type `{}` to display".format(type.name))


    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        
        text = message.content.lower()
        
        # Triggered if forgor appears in the message.
        if "forgor" in text:
            await message.add_reaction("\U0001f480")

        # Triggered on any occurrence of the word "ham".
        parsed = re.search(r"\s*ham($|[ .,!?\-'])", text)
        if parsed is not None:
            await message.add_reaction("<:ham:1061984465548742656>")

        # Triggered on @here or @everyone with message text containing "meeting time".
        if  message.mention_everyone and "meeting" in text:
            await message.add_reaction("<:whygod:1061614468234235904>")
            return

        # Triggered on any occurrence of the substring "sus", or words "among us" or "amogus".
        parsed = re.search(r"sus|\s*(among us|amogus)($|[ .,!?\-'])", text)
        if parsed is not None:
            await message.channel.send("<:sus:1061610886365712464>")
            return

        # Triggered on any occurrence of the word "puzzle"
        parsed = re.search(r"\s*puzzle($|[ .,!?\-'])", text)
        if parsed is not None:
            await message.reply("https://media.tenor.com/PPWUxTjZarsAAAAd/he-he-he-yup-yup.gif")
            return

        # Triggered if message text is "hello?" exactly.
        if text == "hello?":
            await message.channel.send(":musical_note: Is it me you're looking for? :musical_note:")
            return

        # Triggered on any occurrence of the words "get c".
        parsed = re.search(r"\s*get c($|[ .,!?\-'])", text)
        if parsed is not None:
            await message.reply("https://cdn.discordapp.com/emojis/837504400200040498.gif")
            return

        await self.bot.process_commands(message)


    @tasks.loop(minutes=30.0)
    async def scraper_task(self):
        detected = self.scraper.run()
        await botlog.new_threads(detected)

        if detected == 0:
            return

        channel = self.bot.get_channel(int(os.getenv("CHANNEL_ID")))
        threads = self.scraper.get_new_threads()
        count = len([thread for thread in threads if isinstance(thread, Application)])

        self.new_embeds = await self.generate_embeds(self.scraper.get_new_threads())
        self.appeal_embeds = await self.generate_embeds(self.scraper.get_appeal_threads())
        self.application_embeds = await self.generate_embeds(self.scraper.get_application_threads())
        
        ping_staff = ""
        for embed in self.appeal_embeds:
            if embed[1] is not None:
                ping_staff += "<@{}>\n".format(embed[1].id)

        embed = discord.Embed(color=discord.Colour.from_str("#1cb4fa"),
                        title=":incoming_envelope: ***You've got mail !***")

        embed.description = self.seperator + \
                            ":scales: {} new appeal(s)\n".format(len(threads) - count) + \
                            ":pencil: {} new application(s)\n".format(count) + \
                            ":man_detective: 0 new report(s)\n" + \
                            self.seperator + \
                            ":bulb: Use `/viewthreads new`"
        
        if len(ping_staff) > 0:
            await channel.send(ping_staff, embed=embed)
        else:
            await channel.send(embed=embed)

        # Start running the open thread reminder task if not already running.
        if not self.reminder.is_running():
            self.reminder.start()


    # Loops every 7 days.
    @tasks.loop(hours=168)
    async def reminder(self):
        channel = self.bot.get_channel(int(os.getenv("CHANNEL_ID")))
        threads = self.scraper.get_open_threads()

        if len(threads) == 0 or self.reminder.current_loop == 0:
            return

        # Send weekly open thread reminder embed.
        embed = discord.Embed(color=discord.Colour.from_str("#1cb4fa"),
                title=":books: ***Threads need attention***")

        embed.description = self.seperator + ":thread: There are **{}** open thread(s)\n".format(len(threads)) + \
                            self.seperator + \
                            ":bulb: Use `/viewthreads all`"

        await channel.send(embed=embed)
