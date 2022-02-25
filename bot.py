import os
import re
import discord
import dotenv
from utils import get_word, read_history, get_emoji_numbers, get_wordle_results, get_quordle_results
from db import dbcsv

# Load .env file
dotenv.load_dotenv()

# Discord bot client
client   = discord.Client()
wordledb = dbcsv("wordle.csv")
quordldb = dbcsv("quordle.csv")

# Regex
wordle_match_str = r"(Wordle) (\d+) (\d+/\d+)"
wordle_match = re.compile(wordle_match_str)

quordle_match_str = r"(Daily Quordle) \#(\d+)"
quordle_match = re.compile(quordle_match_str)

# Client functions

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):

    # Skip parsing scrugbot message
    if message.author == client.user:
        return

    # Keys
    if message.content == '!scrugbot':
        await message.channel.send(f'Hello {message.author.display_name}!')

    if message.content == '!scrugbot help':
        help_msg = "Use scrugbot as !scrugbot [rebuild|word|wordle]\nScrugbot will also store wordle and quordle results automatically and give you some motivation!\nUse rebuild only if the result databases need to be rebuilt.\nUse word to get a 5 letter word tip.\nUse wordle to see the results of all users!\n"
        await message.channel.send(help_msg)

    if message.content == '!scrugbot rebuild':
        await message.channel.send(f'Rebuilding results')
        await read_history(client, wordledb, wordle_match)
        await read_history(client, quordldb, quordle_match)

    # Wordle - get a word
    if message.content == '!scrugbot word':
        await message.channel.send(f"Why not try ... {get_word()}")

    # Wordle - print results
    if message.content == '!scrugbot wordle':
        await message.channel.send(get_wordle_results())

    # Wordle - print results
    if message.content == '!scrugbot quordle':
        await message.channel.send(get_quordle_results())

    # Wordle responses
    x = wordle_match.match(message.content)
    if x:
        username = message.author.display_name
        wordledb.write([message.id, message.created_at, username, x.groups()[0], x.groups()[1], x.groups()[2]])
        if "1/6" == x.groups()[2]:
            await message.channel.send(f"Amazing work {username}!")
        elif "2/6" == x.groups()[2]:
            await message.channel.send(f"Nice one {username}!")
        elif "3/6" == x.groups()[2]:
            await message.channel.send(f"Good word choice {username}!")
        elif "4/6" == x.groups()[2]:
            await message.channel.send(f"Oof, getting there, {username}!")
        elif "5/6" == x.groups()[2]:
            await message.channel.send(f"That was tough, {username}!")
        elif "6/6" == x.groups()[2]:
            await message.channel.send(f"Squeaked in at the end, {username}!")
        else:
            await message.channel.send(f"Uhh ohh {username}...")

    # Quordle responses
    x = quordle_match.match(message.content)
    if x:
        username = message.author.display_name
        results = get_emoji_numbers(message.content)
        # Total is 4*8 = 32
        total = sum(results)
        quordldb.write([message.id, message.created_at, username, x.groups()[0], x.groups()[1], total])
        if total < 8:
            await message.channel.send(f"Damn, that's some quick quordling {username}!")
        elif total < 16:
            await message.channel.send(f"Pretty decent quordle, {username}!")
        elif total < 24:
            await message.channel.send(f"Managed to stay on top of that, {username}!")
        elif total < 32:
            await message.channel.send(f"Ooo that was tricky, {username}!")
        else:
            await message.channel.send(f"Beaten into submission, {username}...")

    
# Run client
client.run(os.getenv('TOKEN'))