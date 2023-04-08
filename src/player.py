import os
from nbsplayer import Player
from discord.ext import commands


async def setup(bot: commands.Bot):
    cache = os.path.join(os.path.dirname(__file__), os.path.join("..", "cache"))
    nbs = os.path.join(os.path.dirname(__file__), os.path.join("..", "nbs"))
    sounds = os.path.join(os.path.dirname(__file__), os.path.join("..", "sounds"))

    await bot.add_cog(Player(bot, nbs_path=nbs, sound_path=sounds, cache_path=cache))
