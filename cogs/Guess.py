import discord
from discord.ext import commands, tasks
from youtube_dl import YoutubeDL
from youtube_search import YoutubeSearch
import json

class Guess(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.msg = None
        self.index = 0
        self.voice_channel = None
        self.current_song = None
        self.points = {}
        self.song_info = None
        self.data = {
            "Gintama": "https://www.youtube.com/watch?v=aFIhebJ7NaU",
            "March comes in like a lion": "https://www.youtube.com/watch?v=cKWqPXkLgzY",
            "pokemon": "https://www.youtube.com/watch?v=rg6CiPI6h2g",
            "Fruits basket": "https://www.youtube.com/watch?v=dUDSedRJHf4",
            "ya boy kongming": "https://www.youtube.com/watch?v=piEyKyJ4pFg",
            "owarimonogatari": "https://www.youtube.com/watch?v=ieggkmdxa5s",
            "Madoka Magica": "https://www.youtube.com/watch?v=OrgpX-_bFqM",
            "shaman king": "https://www.youtube.com/watch?v=b_ctlDcxZbc",
            "steins;gate": "https://www.youtube.com/watch?v=dd7BILZcYAY",
            "jojos bizzare adventure": "https://www.youtube.com/watch?v=eLwuQwKs4yA",
            "Gundam": "https://www.youtube.com/watch?v=Yn27jQAuoWw",
            "yu-gi-oh": "https://www.youtube.com/watch?v=MjdNz071O4E",
            "Jujutsu kaisen": "https://www.youtube.com/watch?v=i1P-9IspBus",
            "samurai champloo": "https://www.youtube.com/watch?v=Eq6EYcpWB_c",
            "attack on titan": "https://www.youtube.com/watch?v=OBqw818mQ1E",
            "lucky star": "https://www.youtube.com/watch?v=6iseNlvH2_s",
            "death parade": "https://www.youtube.com/watch?v=Ca5Tf5BDSYI",
            "guilty crown": "https://www.youtube.com/watch?v=DjUtmbZt8zc",
            "haikyuu": "https://www.youtube.com/watch?v=XS-N8KfZ5EU",
            "sailor moon": "https://www.youtube.com/watch?v=34ppUaNh2vw",
            "code geass": "https://www.youtube.com/watch?v=G8CFuZ9MseQ",
            "fate/zero": "https://www.youtube.com/watch?v=xDarqGKWwQQ",
            "bakuman": "https://www.youtube.com/watch?v=8vMRheOXO_w",
            "full metal alchemist": "https://www.youtube.com/watch?v=1dNkQoE76nY",
            "dragon ball z": "https://www.youtube.com/watch?v=R4vjJrGeh1c",
            "cowboy bepop": "https://www.youtube.com/watch?v=EL-D9LrFJd4",
            "your lie in april": "https://www.youtube.com/watch?v=H8MyvOcTy6k",
            "neon genesis evangelion": "https://www.youtube.com/watch?v=k8ozVkIkr-g",
        }
        self.YTDL_OPTIONS = {'format': 'bestaudio', 'nonplaylist': 'True'}
        self.songs = [x for x in self.data]
        self.current_song = None

    @tasks.loop(seconds=8.0)
    async def music_loop(self):
        # Stop the stop
        self.voice_channel.stop()
        self.songs = list(self.data.keys())

        self.current_song = self.songs[self.index]
        # Play the next song
        with YoutubeDL(self.YTDL_OPTIONS) as ydl:
            try:
                self.song_info = ydl.extract_info(self.data[self.songs[self.index]], download=False)['formats'][0]['url']
            except:
                await self.msg.send("Song format is wrong")

        self.voice_channel.play(
            discord.FFmpegPCMAudio(executable="C:/ffmpeg/bin/ffmpeg.exe", source=self.song_info)
        )

        self.index += 1

    @music_loop.after_loop
    async def after_music_loop(self):
        # After the loop - Print scores of the users
        points_string = ""
        for x in self.points:
            user = f"<@{x}> : {self.points[x]}"
            points_string += f"{user}\n"
        embed = discord.Embed(title="Points", description=points_string)
        await self.msg.send(embed=embed)

    @music_loop.before_loop
    async def before_music_loop(self):
        self.songs = [self.data.keys()]

    @commands.command()
    async def start_guess(self, msg):
        current_song = self.current_song
        self.msg = msg
        # Join the vc depending on the status of the user
        voice = msg.author.voice

        voice_client = discord.utils.get(msg.bot.voice_clients, guild=msg.guild)
        if voice_client:
            self.voice_channel = voice_client
            await msg.send("Song is currently playing")
        elif not voice:
            await msg.send("You're not in a voice channel, please join one")
        else:
            self.voice_channel = await voice.channel.connect()

        self.music_loop.start()

        @self.bot.event
        async def on_message(ctx):
            if ctx.content.lower() == self.current_song.lower():
                if ctx.author.id in self.points:
                    self.points[ctx.author.id] += 1
                else:
                    self.points[ctx.author.id] = 1

                await ctx.channel.send("Correct!")
            elif ctx.content.lower() == "!stop_guess":
                self.music_loop.stop()
                self.voice_channel.stop()


    @commands.command()
    async def stop_guess(self, msg):
        self.music_loop.stop()
        
def setup(bot):
    bot.add_cog(Guess(bot))