# -*- coding: utf-8 -*-
"""
Created on Mon Feb  1 00:05:09 2021

@author: mocha
"""
# bot.py
import os
import asyncio
import discord
from datetime import datetime
from discord.ext import commands, tasks
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
CHANNEL_GENERAL = os.getenv('CHANNEL_GENERAL')

#has to be a smarter way of doing this lmao
greetings = ["hi bot", "Hi bot", "hello fraux", "Hello Fraux", "hello Fraux", "Hello bot", "hello bot", "hi fraux", "Hi Fraux", "hi Fraux"]

bot = commands.Bot(command_prefix='!')

@bot.command()
async def welcome(ctx):

    response = "weclome to " + GUILD
    await ctx.send(response)


@bot.event
async def on_ready():
    for guild in bot.guilds:
        if guild.name == GUILD:
            break

    print(
        f'{bot.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})\n'
    )

    members = '\n - '.join([member.name for member in guild.members])
    print(f'Guild Members:\n - {members}')
    
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.content in greetings:
        response = "henlo " + message.author.name
        await message.channel.send(response)
    await bot.process_commands(message)


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
    now = datetime.now()
    startTime = datetime.strptime(now.strftime("%H:%M:%S"), '%H:%M:%S')
    targetTime = datetime.strptime('20:00:00', '%H:%M:%S')
    timeDiff = (targetTime - startTime).seconds  
    print("Time diff one is " + str(timeDiff))
    await asyncio.sleep(timeDiff)   
    await bot.wait_until_ready()
    print("Finished waiting")

day_reset_notif.start()
bot.run(TOKEN)