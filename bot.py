import os
import re
import discord
import dotenv
from utils import get_word, read_history, get_emoji_numbers, get_wordle_results, get_quordle_results, get_chatbot_conversation
from db import dbcsv
from music import playlists

# Load .env file
dotenv.load_dotenv()

# Discord bot client
client    = discord.Client()
wordledb  = dbcsv("wordle.csv")
quordldb  = dbcsv("quordle.csv")
playlists = playlists()

# Regex
wordle_match_str = r"(Wordle) (\d+) (\d+/\d+)"
wordle_match = re.compile(wordle_match_str)

quordle_match_str = r"(Daily Quordle) \#(\d+)"
quordle_match = re.compile(quordle_match_str)

# Client functions

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    # Decorate the client with info about running chatbot
    client.active_chatbot = False

@client.event
async def on_message(message):

    # Skip parsing scrugbot message
    if message.author == client.user:
        return

    # Keys
    if message.content == '!scrugbot':
        await message.channel.send(f'Hello {message.author.display_name}!')

    if message.content == '!scrugbot help':
        help_msg = "Use scrugbot as !scrugbot [rebuild|word|wordle|quordle|chat|stop]\nScrugbot will also store wordle and quordle results automatically and give you some motivation!\nUse rebuild only if the result databases need to be rebuilt.\nUse word to get a 5 letter word tip.\nUse wordle|quordle to see the results of all users!\nUse chat to turn on a tester Hagrid chatbot!\nUse stop to deactivate it!\n"
        await message.channel.send(help_msg)

    if message.content == '!scrugbot rebuild':
        await message.channel.send(f'Rebuilding results')
        await read_history(client, wordledb, wordle_match)
        await read_history(client, quordldb, quordle_match, True)

    # Wordle - get a word
    if message.content == '!scrugbot word':
        await message.channel.send(f"Why not try ... {get_word()}")

    # Wordle - print results
    if message.content == '!scrugbot wordle':
        await message.channel.send(get_wordle_results())

    # Wordle - print results
    if message.content == '!scrugbot quordle':
        await message.channel.send(get_quordle_results())

    # Chatbot - get response
    if client.active_chatbot and '!scrugbot' not in message.content:
        async with message.channel.typing():
            response = await get_chatbot_conversation(message)
        bot_response = response.get('generated_text', None)
        if not bot_response:
            if 'error' in response:
                bot_response = '`Error: {}`'.format(response['error'])
            else:
                bot_response = 'Hmm... something is not right.'
        await message.channel.send(bot_response)
    
    # Chatbot - On
    if message.content == '!scrugbot chat':
        client.active_chatbot = True
        await message.channel.send("scrugbot is sentient")
    # Chatbot - Off
    if message.content == '!scrugbot stop':
        client.active_chatbot = False
        await message.channel.send("scrugbot is dumb")

    # Playlists
    if message.content.startswith('!scrugbot add '):
        c = message.content.split("!scrugbot add ")[1]
        p = c.split()[0].strip()
        s = " ".join(c.split()[1:]).strip()
        playlists.add_entry(p,s)

    if message.content == '!scrugbot list':
        await message.channel.send(playlists.list_playlists())

    if message.content == '!scrugbot songs':
        await message.channel.send(playlists.list_songs())

    if message.content.startswith('!scrugbot playlist '):
        p = message.content.split('!scrugbot playlist')[1].strip()
        await message.channel.send(playlists.list_songs_from_playlist(p))

    if message.content.startswith('!scrugbot play '):
        nsongs = message.content.split("!scrugbot play ")[1]
        await message.channel.send(playlists.get_random_songs(nsongs))

    if message.content == '!scrugbot play':
        await message.channel.send(playlists.get_random_songs())

    # Wordle responses
    x = wordle_match.match(message.content)
    if x:
        username = message.author.display_name
        wordledb.write([message.id, message.created_at, message.author.name, x.groups()[0], x.groups()[1], x.groups()[2]])
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
        quordldb.write([message.id, message.created_at, message.author.name, x.groups()[0], x.groups()[1], total])
        if total < 11:
            await message.channel.send(f"Damn, that's some quick quordling {username}!")
        elif total < 16:
            await message.channel.send(f"Wow, decent quordle, {username}!")
        elif total < 21:
            await message.channel.send(f"Pretty good work, {username}!")
        elif total < 26:
            await message.channel.send(f"Managed to stay on top of that, {username}!")
        elif total < 31:
            await message.channel.send(f"Ooo that was tricky, {username}!")
        else:
            await message.channel.send(f"Beaten into submission, {username}...")

    
# Run client
client.run(os.getenv('TOKEN'))