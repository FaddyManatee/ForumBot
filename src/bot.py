# Standard library imports.
import os
import json
import re
import base64

# Third-party imports.
import discord
from discord.ext import commands, tasks
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from dotenv import load_dotenv

# Custom imports.
import botlog
import forum
import scraper
from paginator import Paginator


"""
bot.py

Implements bot functionality.

Slash commands, reactions, etc.
"""


load_dotenv()


async def setup(bot: commands.Bot):
    await bot.add_cog(Bot(bot))


class Bot(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.cookie_msg_sent = False
        self.cookie_msg_id = ""
        self.main_channel = int(os.getenv("CHANNEL_ID"))
        self.owner_id = int(os.getenv("OWNER_ID"))
        self.scraper = scraper.Scraper()
        self.seperator = "---------------------------------"
    

    async def check_user_authorised(self, id: int) -> bool:
        # Load the staff.json file.
        with open("staff.json", "r") as f:
            data = json.load(f)

        # Iterate through the staff list and check if the ID matches.
        for staff_member in data["staff"]:
            if staff_member["discord"] == id:
                return True

        # If no match is found, return False.
        return False


    async def generate_embeds(self, threads: list[forum.Thread]) -> list[discord.Embed]:
        embeds = []

        for thread in threads:
            embeds.append(thread.to_embed())
        
        return embeds
    

    async def notify_new_threads(self):
        appeals = self.scraper.get_new_appeal_threads()
        applications = self.scraper.get_new_application_threads()
        reports = self.scraper.get_new_report_threads()

        # Collect moderators to ping.
        moderators = {appeal.get_moderator() for appeal in appeals}
        to_ping = "New appeals for:\n" + '\n'.join(moderators)

        # Prepare embed description dynamically, only adding non-zero counts.
        description_lines = []

        if len(appeals) > 0:
            word = "appeal" if len(appeals) == 1 else "appeals"
            description_lines.append(f":scales: {len(appeals)} new {word}")

        if len(applications) > 0:
            word = "application" if len(applications) == 1 else "applications"
            description_lines.append(f":pencil: {len(applications)} new {word}")

        if len(reports) > 0:
            word = "report" if len(reports) == 1 else "reports"
            description_lines.append(f":man_detective: {len(reports)} new {word}")

        embed_new_threads = discord.Embed(color=discord.Colour.from_str("#1cb4fa"), title=":incoming_envelope: ***New threads found!***")
        embed_new_threads.description = f"{self.seperator}\n" + "\n".join(description_lines) + f"\n{self.seperator}\n:bulb: Use `/viewthreads`"

        # Send the notification.
        channel = self.bot.get_channel(self.main_channel)
        await channel.send(to_ping, embed=embed_new_threads)


    async def notify_new_posts(self):
        posts = self.scraper.get_new_posts()
        result = ""

        for thread, new_posts in posts.items():
            result += f"**{thread.get_title()}**\n"
            
            for post in new_posts:
                post_url = thread.get_url() + "#" + post.get_id()
                result += f"[New post]({post_url}) by {post.get_author()}\n"

        embed_new_posts = discord.Embed(color=discord.Colour.from_str("#1cb4fa"), title=":incoming_envelope: ***New posts found!***")
        embed_new_posts.description = f"{self.seperator}\n" + result + self.seperator

        # Send the notification.
        channel = self.bot.get_channel(self.main_channel)
        await channel.send(embed=embed_new_posts)


    @discord.app_commands.command(name="viewthreads", description="View forum threads that still need to be closed")
    @discord.app_commands.describe(type="Filter threads based on their type")
    @discord.app_commands.choices(type=[
        discord.app_commands.Choice(name="appeal",      value=2),
        discord.app_commands.Choice(name="application", value=3),
        discord.app_commands.Choice(name="report",      value=4)
    ])
    async def view_threads(self, interaction: discord.Interaction, type: int = 1):
        # Check that the user's ID is authorised to use this command.
        authorised = await self.check_user_authorised(interaction.user.id)
        
        if not authorised:
            await interaction.response.send_message("You are not authorised to use this command!", ephemeral=True)
            return

        type_choices = ["all", "appeal", "application", "report"]

        await botlog.command_used(interaction.user.name, interaction.command.name + " " + type_choices[type - 1])

        embeds = None

        match type:
            case 1:
                embeds = await self.generate_embeds(self.scraper.get_all_threads())
            case 2:
                embeds = await self.generate_embeds(self.scraper.get_appeal_threads())
            case 3:
                embeds = await self.generate_embeds(self.scraper.get_application_threads())
            case 4:
                embeds = await self.generate_embeds(self.scraper.get_report_threads())
        
        try:
            # Create custom buttoms to override default paginator button appearance.
            next_button = discord.ui.Button(label="\u25ba", style=discord.ButtonStyle.primary)
            prev_button = discord.ui.Button(label="\u25c4", style=discord.ButtonStyle.primary)
            
            paginator = Paginator(
                next_button=next_button,
                previous_button=prev_button,
                delete_on_timeout=True,
                ephemeral=True
            )

            await paginator.start(interaction, embeds)

        except ValueError:
            await interaction.response.send_message(f"There are no open threads of type `{type_choices[type - 1]}` to display", ephemeral=True)


    @discord.app_commands.command(name="cookie", description="Update the session cookie used to access the forums")
    @discord.app_commands.describe(data="Provide the encrypted session cookie data",
                                   confirmation="Are you sure that the session cookie you have provided is properly encrypted?"
    )
    @discord.app_commands.choices(confirmation=[discord.app_commands.Choice(name="yes", value=1)])
    async def update_cookie(self, interaction: discord.Interaction, data: str, confirmation: int):
        if interaction.user.id != self.owner_id:
            await interaction.response.send_message("You must be the bot owner to use this command!", ephemeral=True)
            return
        
        # Load the bot's private key.
        with open("private_key.pem", "rb") as f:
            private_key = serialization.load_pem_private_key(f.read(), password=None)

        # Decrypt the session cookie.
        decrypted = private_key.decrypt(
            base64.b64decode(data),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        # Convert decrypted data back to string.
        result = decrypted.decode(encoding="utf-8")
        self.scraper.set_session_cookie(result)
        await interaction.response.send_message("The session cookie has been updated successfully!", ephemeral=True)
        await self.cookie_msg_id.delete()


    # Display changelog.md in an embed.
    @discord.app_commands.command(name="changelog", description="View ForumBot version changelog")
    async def changelog(self, interaction: discord.Interaction):
        await botlog.command_used(interaction.user.name + "#" + interaction.user.discriminator,
                                  interaction.command.name)
        
        embed = discord.Embed(color=discord.Colour.from_str("#fff49c"), title="ForumBot Changelog")

        embed.description = open("changelog.md", "r").read()

        # Find latest version string and display in footer.
        embed.set_footer(text="Version {} by FaddyManatee".format(re.findall(r"\d\.\d\.\d", embed.description)[-1]),
                icon_url="https://i.postimg.cc/jqknFJzc/83710a88d36d8c7b42e0d337cb4adc12.jpg")
        await interaction.response.send_message(embed=embed, ephemeral=True)


    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        
        text = message.content.lower()

        # Triggered on @here or @everyone with message text containing "meeting".
        if message.mention_everyone and "meeting" in text:
            await message.add_reaction("<:whygod:1061614468234235904>")

        # Triggered on any occurrence of sussy strings.
        parsed = re.search(r"sus|\s*(among us|amogus|amongus|jerma)($|[ .,!?\-'])", text)
        if parsed is not None:
            await message.channel.send("<:sus:1061610886365712464>")


    @commands.Cog.listener()
    async def on_ready(self):
        print("Logged in as {0.user}".format(self.bot))

        # Sync the command tree globally on startup.
        await self.bot.tree.sync()
        print("Command tree synced!")

        # Start task to periodically execute Scraper.run()
        if not self.scraper_task.is_running():
            self.scraper_task.start()


    @tasks.loop(minutes=5.0)
    async def scraper_task(self):
        try:
            result = self.scraper.run()
            new_threads = result[0]
            new_posts = result[1]

            await botlog.new_threads(new_threads)

            if new_threads == 0 and new_posts == 0:
                return

            if new_threads > 0:
                await self.notify_new_threads()

            if new_posts > 0:
                await self.notify_new_posts()

            # Start the open thread reminder task if not already running.
            if not self.reminder.is_running():
                self.reminder.start()

            self.cookie_msg_sent = False

        except scraper.InvalidCookieError:
            await botlog.invalid_cookie()

            if not self.cookie_msg_sent:
                channel = self.bot.get_channel(self.main_channel)
                self.cookie_msg_sent = True
                self.cookie_msg_id = await channel.send(f"Help! I can't access the forums <@{self.owner_id}>")
            

    # Loops every 7 days.
    @tasks.loop(hours=168)
    async def reminder(self):
        channel = self.bot.get_channel(self.main_channel)
        threads = self.scraper.get_all_threads()

        if len(threads) == 0 or self.reminder.current_loop == 0:
            return

        # Send weekly open thread reminder embed.
        embed = discord.Embed(color=discord.Colour.from_str("#1cb4fa"),
                title=":books: ***Threads need attention!***")
        
        word_1 = "is" if len(threads) == 1 else "are"
        word_2 = "thread" if len(threads) == 1 else "threads"

        embed.description = self.seperator + \
                            f"\n:thread: There {word_1} **{len(threads)}** open {word_2}...\n" + \
                            self.seperator + \
                            "\n:bulb: Use `/viewthreads`"

        await channel.send(embed=embed)
