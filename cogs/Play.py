import discord
from discord.ext import commands
from youtube_dl import YoutubeDL
import requests

class Play(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = []
        self.current_index = 0
        self.current_vc = None
        self.song_info = ""
        self.YTDL_OPTIONS = {'format': 'bestaudio', 'nonplaylist': 'True'}

    @commands.command()
    async def add(self, msg, url:str):
        self.queue.append(url)
        await msg.send(f"Song added to the queue, position: {len(self.queue)}")

    @commands.command()
    async def pause(self, msg):
        self.current_vc.pause()
        await msg.send("Song paused")

    @commands.command()
    async def resume(self, msg):
        self.current_vc.resume()
        await msg.send("Song resumed")

    @commands.command()
    async def stop(self, msg):
        self.current_vc.stop()
        await self.current_vc.disconnect()
        self.current_vc = None

        await msg.send("Stopped playing music")

    @commands.command()
    async def play(self, msg, url:str):
        voice = msg.author.voice

        voice_client = discord.utils.get(msg.bot.voice_clients, guild=msg.guild)
        if voice_client:
            self.current_vc = voice_client
            await msg.send("Song is currently playing")
        elif not voice:
            await msg.send("You're not in a voice channel, please join one")
        else:
            self.current_vc = await voice.channel.connect()

        self.queue[0:0] = [url]
        self.current_index = 0

        #self.song_info = self.extract_info(self, url)

        with YoutubeDL(self.YTDL_OPTIONS) as ydl:
            try:
                self.song_info = ydl.extract_info(url, download=False)['formats'][0]['url']
            except:
                await msg.send("Song format is wrong")


        self.current_vc.play(
            discord.FFmpegPCMAudio(executable="C:/ffmpeg/bin/ffmpeg.exe", source=self.song_info)
        )

    @commands.command()
    async def next(self, msg):
        if self.current_index == len(self.queue):
            self.current_index = 0
        else:
            self.current_index += 1

        self.current_vc.stop()

        #self.song_info = self.extract_info(self, self.queue[self.current_index])

        with YoutubeDL(self.YTDL_OPTIONS) as ydl:
            try:
                self.song_info = ydl.extract_info(self.queue[self.current_index], download=False)['formats'][0]['url']
            except:
                await msg.send("Song format is wrong")

        self.current_vc.play(
            discord.FFmpegPCMAudio(executable="C:/ffmpeg/bin/ffmpeg.exe", source=self.song_info)
        )

        await msg.send(f"Song skipped. Currently playing: {self.queue[self.current_index]}")

    @commands.command()
    async def previous(self, msg):
        if self.current_index == 0:
            self.current_index = len(self.queue)-1
        else:
            self.current_index -= 1

        if self.current_index < 0:
            self.current_index = 0
            await msg.send("Previous song not possible")
            return

        self.current_vc.stop()

        with YoutubeDL(self.YTDL_OPTIONS) as ydl:
            try:
                self.song_info = ydl.extract_info(self.queue[self.current_index], download=False)['formats'][0]['url']
            except:
                await msg.send("Song format is wrong")

        self.current_vc.play(
            discord.FFmpegPCMAudio(executable="C:/ffmpeg/bin/ffmpeg.exe", source=self.song_info)
        )

        await msg.send(f"Song skipped. Currently playing: {self.queue[self.current_index]}")

    @commands.command()
    async def queue(self, msg):
        await msg.send(f"Queue length: {len(self.queue)}, Curret song index: {self.current_index}")

def setup(bot):
    bot.add_cog(Play(bot))