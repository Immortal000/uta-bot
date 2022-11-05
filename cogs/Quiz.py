import discord
from discord.ext import commands

class Quiz(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.command()
    async def start_quiz(self, ctx):
        return

    @commands.command()
    async def next_question(self, ctx):
        return

    @commands.command()
    async def stop_quiz(self, ctx):
        return

def setup(bot):
    bot.add_cog(Quiz(bot))