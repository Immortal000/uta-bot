import discord
from discord.ext import commands, tasks
import random

class Quiz(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.info = {
            "Who was the first woman to kiss Luffy?": "Reiju",
            "Who was the first Admiral to be shown in the series?": "Aokiji",
            "Who gave Shanks the scar on his eye?": "Blackbeard",
            "How many crewmates did Luffy say he wanted at the beginning of the series?":"10",
            "Luffy got the Straw Hat from Gol D. Roger. Is this statement true or false?": "False",
            "Akainu lost in his battle against Kuzan for Fleet Admiral. State true or false.":"False",
            "Sanji will only attack women if they harm his friends. State true or false.":"False",
            "Brook is the oldest current SH member. State true or false. ":"True",
            "Who said the Zoro should cut diamond next?": "Daz Bones",
            "Who was the first recruit of the SH crew?": "Zoro",
            "Who promised that they would never lose another fight until they defeated a certain someone?": "Zoro",
            "How did Luffy get the scar under his eye?": "Himself",
            "Who was the first member of the SH crew to try and recruit a new member besides Luffy?": "Nami",
            "Who was the first villain to defeat Luffy?":"Crocodile",
            "What made Crocodile join Luffys 'Rescue Ace Crew'?": "Ivanknov"
        }
        self.questions = [x for x in self.info]
        self.current_question = ""
        self.current_answer = ""
        self.points = {}
    @tasks.loop(seconds = 8.0)
    async def quiz_loop(self):
        self.current_question = random.choice(self.questions)
        self.questions.remove(self.current_question)
        self.current_answer = self.info[self.current_question]
        await self.ctx.send(self.current_question)

    @quiz_loop.after_loop
    async def after_quiz_loop(self):
        await self.ctx.send("Quiz stopped")

    @commands.command()
    async def start_quiz(self, ctx):
        self.ctx = ctx

        self.quiz_loop.start()

        @self.bot.event
        async def on_message(ctx):
            print(self.current_answer)
            if ctx.content.lower() == self.current_answer.lower():
                if ctx.author.id in self.points:
                    self.points[ctx.author.id] += 1
                else:
                    self.points[ctx.author.id] = 1

                await ctx.channel.send("Correct!")
            elif ctx.content.lower() == "!stop_quiz":
                points_string = ""
                for x in self.points:
                    user = f"<@{x}> : {self.points[x]}"
                    points_string += f"{user}\n"
                embed = discord.Embed(title="Points", description=points_string)
                await self.ctx.send(embed=embed)
                self.quiz_loop.stop()

    @commands.command()
    async def stop_quiz(self, ctx):
        self.quiz_loop.stop()
        ctx.send("Quiz stopped!")

def setup(bot):
    bot.add_cog(Quiz(bot))