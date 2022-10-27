import discord
from discord.ext import commands

class Guess(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        
def setup(bot):
    bot.add_cog(Guess(bot))