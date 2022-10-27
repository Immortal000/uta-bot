import discord
from discord.ext import commands

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.command()
    async def ping(self, msg):
        await msg.send("Pong!")

def setup(bot):
    bot.add_cog(Utility(bot))