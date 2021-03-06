# -*- coding: utf-8 -*-
"""
Created on Mon Feb  1 00:05:09 2021

@author: mocha
"""
# bot.py
import os
import asyncio
import discord
import random
from datetime import datetime
from discord.ext import commands, tasks
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
CHANNEL_GENERAL = os.getenv('CHANNEL_GENERAL')
CHANNEL_DELETED_MSGS = os.getenv('CHANNEL_DELETED_MSGS')

#has to be a smarter way of doing this lmao
greetings = ["hi bot", "Hi bot", "hello fraux", "Hello Fraux", "hello Fraux", "Hello bot", "hello bot", "hi fraux", "Hi Fraux", "hi Fraux"]

bot = commands.Bot(command_prefix='!')



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
