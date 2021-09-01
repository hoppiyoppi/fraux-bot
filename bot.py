# -*- coding: utf-8 -*-
"""
Created on Mon Feb  1 00:05:09 2021

@author: mocha
"""
# bot.py
import os
import time
import asyncio
import discord
import random
import youtube_dl
from datetime import datetime
from datetime import timezone
from discord.ext import commands, tasks
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
CHANNEL_GENERAL = os.getenv('CHANNEL_GENERAL')
CHANNEL_DELETED_MSGS = os.getenv('CHANNEL_DELETED_MSGS')

#has to be a smarter way of doing this lmao
greetings = ["hi bot", "Hi bot", "hello fraux", "Hello Fraux", "hello Fraux", "Hello bot", "hello bot", "hi fraux", "Hi Fraux", "hi Fraux"]

musicQueue = []

bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"))


youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0', # bind to ipv4 since ipv6 addresses cause issues sometimes
    'extension': 'mp3'
}

ffmpeg_options = {
    'options': '-y -vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def play(self, ctx, *, query):
        """Plays a file from the local filesystem"""


        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(query))
        if ctx.voice_client.is_playing():
            musicQueue.append(source)
            await ctx.send('Added to queue')
        else:
            ctx.voice_client.play(source, after=lambda e: print(f'Player error: {e}') if e else None)
            await ctx.send(f'Now playing: {query}')

    @commands.command()
    async def yt(self, ctx, *, url):
        """Plays from a url (almost anything youtube_dl supports)"""

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop)
            if ctx.voice_client.is_playing():
                musicQueue.append(player)
                await ctx.send('Added to queue')
            else:
                ctx.voice_client.play(player, after=lambda e: print(f'Player error: {e}') if e else ctx.voice_client.play(musicQueue[0], after=lambda e: print(f'Player error: {e}') if e else None))
                await ctx.send(f'Now playing: {player.title}')
        

    @commands.command()
    async def stream(self, ctx, *, url):
        """Streams from a url (same as yt, but doesn't predownload)"""

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            ctx.voice_client.play(player, after=lambda e: print(f'Player error: {e}') if e else None)

        await ctx.send(f'Now playing: {player.title}')
        

    @commands.command()
    async def volume(self, ctx, volume: int):
        """Changes the player's volume"""

        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel.")

        ctx.voice_client.source.volume = volume / 100
        await ctx.send(f"Changed volume to {volume}%")

    @commands.command()
    async def stop(self, ctx):
        """Stops and disconnects the bot from voice"""
        await ctx.voice_client.disconnect()
        time.sleep(5)
        files_in_directory = os.listdir()
        filtered_files = [file for file in files_in_directory if file.endswith(".webm") or file.endswith(".m4a")]
        for file in filtered_files:
        	path_to_file = os.path.join("", file)
        	os.remove(path_to_file)
        
        

    @play.before_invoke
    @yt.before_invoke
    @stream.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")
        #elif ctx.voice_client.is_playing(): #we handle this in the definition of the play commands
            #source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(query))
            #musicQueue.append(source)
            #await ctx.send('Added to queue')
            #ctx.voice_client.stop()

@bot.command(name='join', help='Tells the bot to join the voice channel')
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send("{} is not connected to a voice channel".format(ctx.message.author.name))
        return
    else:
        channel = ctx.message.author.voice.channel
    await channel.connect()


@bot.command()
async def welcome(ctx):

    response = "weclome to " + GUILD
    await ctx.send(response)


@bot.command()
async def helpme(ctx):

    response = "I am Fraux Bot! Here are my current commands:\n!welcome to send a welcome message\n!bless to send luck for your gacha rolls!\nMy repo is at https://github.com/hoppiyoppi/fraux-bot\nFor questions, contact @hoppiyoppi#1863"
    await ctx.send(response)
    
@bot.command()
async def bless(ctx):

    response = "Good rolls coming your way!"
    await ctx.send(response)
    await ctx.send(file=discord.File('frauxPat.png'))


@bot.event
async def on_ready():

    #set status
    await bot.change_presence(activity=discord.Game(name='!helpme for info'))
    
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.content in greetings:
        response = "henlo " + message.author.name
        await message.channel.send(response)
        
    #thanks to kite for adding this! we'll get you on github eventually...
    if (message.content.startswith("fraux") or message.content.startswith("Fraux")) and message.content.endswith("?"):
        answers = random.randint(1,6)
        if answers == 1:
            await message.channel.send("yes")
        elif answers == 2:
            await message.channel.send("no")
        elif answers == 3:  
            await message.channel.send("maybe") 
        elif answers == 4:
            await message.channel.send("probably")
        elif answers == 5:
            await message.channel.send("probably not")
        elif answers == 6:
            await message.channel.send("i'm not sure...")
    
    await bot.process_commands(message)

@bot.event
async def on_raw_message_delete(payload):
    response = "Author is: " + str(payload.cached_message.author) + "\nContent is: "+ str(payload.cached_message.content) + "\nChannel: " + str(payload.cached_message.channel) + "\nSent at: " + str(payload.cached_message.created_at)
    
    message_channel = bot.get_channel(int(CHANNEL_DELETED_MSGS))
    await message_channel.send(response)

target_channel_id = CHANNEL_GENERAL

@tasks.loop(hours=24)
async def day_reset_notif():
    # nowNow = datetime.now()
    global now
    global startTime
    global targetTime
    global timeDiff
    

    message_channel = bot.get_channel(int(target_channel_id))
    print(f"Got channel {message_channel}")
    print("it is now " + str(targetTime) +"\n it has been " + str(timeDiff//60) + " minutes since the bot started running")
    await message_channel.send("it's day reset!")
    print("day notif done yey yey")

@day_reset_notif.before_loop
async def before():
    global now
    global startTime
    global targetTime
    global timeDiff
    now = datetime.now(tz=timezone.utc)
    startTime = datetime.strptime(now.strftime("%H:%M:%S"), '%H:%M:%S')
    targetTime = datetime.strptime('20:00:00', '%H:%M:%S')
    timeDiff = (targetTime - startTime).seconds  
    print("Time diff one is " + str(timeDiff))
    await asyncio.sleep(timeDiff)   
    await bot.wait_until_ready()
    print("Finished waiting")

day_reset_notif.start()
bot.add_cog(Music(bot))
bot.run(TOKEN)
