import os
os.system("pip3 install discord.py")
from keep_alive import keep_alive
import discord
#from dotenv import load_dotenv
import requests
import json
import re

from db import dbcsv

# Load .env file
#load_dotenv()

# Discord bot client
client = discord.Client()
wordledb = dbcsv("wordle.csv")

# Utils

wordle_match_str = r"(Wordle) (\d+) (\d+/\d+)"
wordle_match = re.compile(wordle_match_str)

def get_word():
    # Get a 5 letter word
    response = requests.get("https://random-word-api.herokuapp.com/word?number=15")
    json_data = json.loads(response.text)
    for x in json_data:
        if len(x) == 5:
            return x
    return get_word()

async def read_history():
    # Function to read history
    og_id = 775730957985906718
    channel = client.get_channel(og_id)
    print (channel)
    messages = await channel.history(limit=1000).flatten()
    for m in messages:
        x = wordle_match.match(m.content)
        if x:
            # print (m.id, m.created_at, m.author, m.content)
            # print (x.groups())
            print (m.id)
            wordledb.write([m.id,m.created_at, m.author.display_name, x.groups()[0],x.groups()[1],x.groups()[2]])
    
# Client functions

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    # To turn on rebuilding the wordle csv
    # await read_history()

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # Keys
    if message.content == '!scrugbot':
        await message.channel.send(f'Hello {message.author.display_name}!')

    # Wordle responses
    if "Wordle" in message.content:
        if "1/6" in message.content:
            await message.channel.send(f"Amazing work {message.author.display_name}!")
        elif "2/6" in message.content:
            await message.channel.send(f"Nice one {message.author.display_name}!")
        elif "3/6" in message.content:
            await message.channel.send(f"Good word choice {message.author.display_name}!")
        elif "4/6" in message.content:
            await message.channel.send(f"Oof, getting there, {message.author.display_name}!")
        elif "5/6" in message.content:
            await message.channel.send(f"That was tough, {message.author.display_name}!")
        elif "6/6" in message.content:
            await message.channel.send(f"Squeaked in at the end, {message.author.display_name}!")
        else:
            await message.channel.send(f"Uhh ohh {message.author.display_name}...")

    x = wordle_match.match(m.content)
    if x:
        wordledb.write([m.id,m.created_at, m.author.display_name, x.groups()[0],x.groups()[1],x.groups()[2]])

    # Wordle - get a word
    if message.content.startswith("!scrugbot"):
        if "word" in message.content:
            await message.channel.send(f"Why not try ... {get_word()}")

# Run client
keep_alive()
client.run(os.getenv('TOKEN'))