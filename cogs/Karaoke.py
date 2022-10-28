import discord
from discord.ext import commands
from youtube_search import YoutubeSearch
from pydub import AudioSegment
from pydub.playback import play
import json
from youtube_dl import YoutubeDL
from scipy.io.wavfile import read, write
import io
import os
import requests
import audiofile
import pytube

class Karaoke(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.current_vc = None
        self.connections = {}
        self.files = None
        self.song_info = None
        self.YTDL_OPTIONS = {'format': 'bestaudio', 'nonplaylist': 'True'}
        self.message_id = None
        self.karaoke_song = None
        self.msg = None


    async def once_done(self, sink: discord.sinks, channel: discord.TextChannel, *args):

        recorded_users = [  # A list of recorded users
            f"<@{user_id}>"
            for user_id, audio in sink.audio_data.items()
        ]

        files = [discord.File(audio.file, f"{user_id}.{sink.encoding}") for user_id, audio in sink.audio_data.items()]  # List down the files.

        self.files = files
        sent_audio_message = await channel.send(f"finished recording audio for: {', '.join(recorded_users)}.", files=files)
        self.message_id = sent_audio_message.id

        await self.msg.invoke(self.bot.get_command('merge'))

        with open(f"./karaoke_mixes/{self.msg.author.id}/final.mp3", 'rb') as fd:
            contents = fd.read()

        contents = io.BytesIO(contents)

        await self.msg.send(files=[discord.File(contents, f"your_beautiful_singing.mp3")])

    @commands.command()
    async def lyrics(self, msg):
        #print(dir(msg.message))
        query = " ".join(msg.message.content.split()[1:])
        print(query)

    @commands.command()
    async def merge(self, msg):
        message = await msg.fetch_message(self.message_id)

        for attachment in message.attachments:
            await attachment.save(f"./karaoke_mixes/{self.msg.author.id}/recordings/{attachment.filename}")

        sound1 = None

        for file in os.listdir(f"./karaoke_mixes/{self.msg.author.id}/recordings"):
            if sound1:
                sound1 = sound1.overlay(AudioSegment.from_mp3(f"./karaoke_mixes/{self.msg.author.id}/recordings/{file}"))
            else:
                sound1 = AudioSegment.from_mp3(f"./karaoke_mixes/{self.msg.author.id}/recordings/{file}")


        # await message.attachments[0].save("voice_recording.mp3")

        # Get the 2 sounds: karaoke and user singing
        sound2 = AudioSegment.from_file(f"./karaoke_mixes/{self.msg.author.id}/karaoke_song.mp3")

        sound2 = sound2 - 10

        # Overlay the songs
        played_togther = sound1.overlay(sound2)
        played_togther.export(f"./karaoke_mixes/{self.msg.author.id}/final.mp3", format="mp3")

    @commands.command()
    async def convert(self, msg, query:str):
        video = query
        data = pytube.YouTube(video)

        # Converts the youtube video to an audio file
        sound = data.streams.get_audio_only()
        sound.download(filename="karaoke_song.mp3", output_path=f"./karaoke_mixes/{self.msg.author.id}")

        # Saves the karaoke song to the local machine
        with open(f"./karaoke_mixes/{self.msg.author.id}/karaoke_song.mp3", 'rb') as fd:
            contents = fd.read()

        # Converts the file into bytes for discord to read
        contents = io.BytesIO(contents)

        self.karaoke_song = contents

        parent_dir = f"D:/programming/bots/uta-py/karaoke_mixes/{self.msg.author.id}"
        directory = "recordings"

        path = os.path.join(parent_dir, directory)

        if not os.path.exists(path):
            os.mkdir(path)

        # Send the karaoke song on discord
        await msg.send(files=[discord.File(contents, f"Karaoke_version.mp3")])

    @commands.command()
    async def record(self, ctx):
        # Joins vc based on where the author of the message is
        voice = ctx.author.voice

        voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
        if voice_client:
            self.current_vc = voice_client
            await ctx.send("Song is currently playing")
        elif not voice:
            await ctx.send("You're not in a voice channel, please join one")
        else:
            self.current_vc = await voice.channel.connect()

        # Updates the connections
        self.connections.update({ctx.guild.id: self.current_vc})

        # Starts recording
        self.current_vc.start_recording(
            discord.sinks.MP3Sink(),
            self.once_done,
            ctx.channel
        )
        await ctx.send("Started recording!")

    @commands.command()
    async def stop_recording(self, ctx):
        if ctx.guild.id in self.connections:
            self.current_vc.stop_recording()
            del self.connections[ctx.guild.id]
            await ctx.send("Stopped recording")
        else:
            await ctx.respond("I am currently not recording here.")

    @commands.command()
    async def karaoke(self, msg, query):
        await msg.send("Say \"Start\" as soon as the text says \"Started recording\". The karaoke version of the song is going to play on the vc and you can start singing whenever you want")
        self.msg = msg
        # Join a vc according to what the user is in
        voice = msg.author.voice

        voice_client = discord.utils.get(msg.bot.voice_clients, guild=msg.guild)
        if voice_client:
            self.current_vc = voice_client
            await msg.send("Song is currently playing")
        elif not voice:
            await msg.send("You're not in a voice channel, please join one")
        else:
            self.current_vc = await voice.channel.connect()

        # Gets the youtube search results
        results = YoutubeSearch(f"{query} karaoke", max_results=10).to_json()
        url_suffix = json.loads(results)["videos"][0]["url_suffix"]
        if url_suffix:
            self.song_info = f"https://www.youtube.com{url_suffix}"
        else:
            await msg.send("No results found")

        # Download the youtube song
        with YoutubeDL(self.YTDL_OPTIONS) as ydl:
            try:
                self.song_info = ydl.extract_info(self.song_info, download=False)['formats'][0]['url']
            except:
                await msg.send("Song format is wrong")


        # Downloads the youtube karaoke to the local machine
        await msg.invoke(self.bot.get_command('convert'), query=f"https://www.youtube.com{url_suffix}")

        # Start the recording
        await msg.invoke(self.bot.get_command('record'))

        # Plays the karaoke
        self.current_vc.play(
            discord.FFmpegPCMAudio(executable="C:/ffmpeg/bin/ffmpeg.exe", source=self.song_info)
        )



def setup(bot):
    bot.add_cog(Karaoke(bot))