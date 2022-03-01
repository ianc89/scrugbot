import os
import re
import discord
import dotenv
from utils import get_word, read_history, get_emoji_numbers, get_wordle_results, get_quordle_results, get_chatbot_conversation
from db import dbcsv
from music import playlists

# Using command decorators
from discord.ext import commands

# Our bot operator
bot = commands.Bot(command_prefix='$', help_command=None)

# Load .env file
dotenv.load_dotenv()

# Discord bot client
client    = discord.Client()

# Databases
wordledb  = dbcsv("wordle.csv")
quordldb  = dbcsv("quordle.csv")
playlists = playlists()

# Regex
wordle_match_str = r"(Wordle) (\d+) (\d+/\d+)"
wordle_match = re.compile(wordle_match_str)

quordle_match_str = r"(Daily Quordle) \#(\d+)"
quordle_match = re.compile(quordle_match_str)


# Help information
@bot.command()
async def help(ctx):
    # Help message function
    options = {
    "usage": "!scrugbot [setting] [optional]",
    "info": "Scrugbot will store wordle and quordle results automatically",
    "rebuild":"Rebuild the word game databases",
    "word":"Get a 5 letter word suggestion",
    "wordle":"Display wordle results",
    "quordle":"Display quordle results",
    "chat":"Turn on the Hagrid chatbot",
    "stop":"Turn off the Hagrid chatbot",
    "add [playlist] [song]":"Add a [song] to the [playlist]",
    "list":"List all stored playlist names",
    "songs":"List all songs and playlists",
    "playlist [playlist]":"List all songs in [playlist]",
    "play [nsongs]":"Get [nsongs] randomly selected from the playlists",
    }
    ret_str = "```HELP for SCRUGBOT\n"
    for topic in options:
        ret_str += topic.ljust(25) + ": " + options[topic] + "\n"
    ret_str += "```"

    # Send message back
    await ctx.send(ret_str)

# Greeting
@bot.command()
async def hello(ctx):
    await ctx.send(f'Hello {ctx.message.author.display_name}!')

# Rebuild function
@bot.command()
async def rebuild(ctx):
    await ctx.send('Rebuilding results')
    await read_history(client, wordledb, wordle_match)
    await read_history(client, quordldb, quordle_match, True)
    await ctx.send('Finished rebuild request')

# Word function
@bot.command()
async def word(ctx):
    await ctx.send(f"Why not try ... {get_word()}")

# Wordle results function
@bot.command()
async def wordle(ctx):
    await ctx.send(get_wordle_results())

# Quordle results function
@bot.command()
async def quordle(ctx):
    await ctx.send(get_quordle_results())

# Chatbot functions
# Turn on
@bot.command()
async def chat(ctx):
    client.active_chatbot = True
    await ctx.send("scrugbot is sentient")

# Turn off
@bot.command()
async def stop(ctx):
    client.active_chatbot = False
    await ctx.send("scrugbot is dumb")

# Ask
@bot.command()
async def ask(ctx, *args):
    async with ctx.message.channel.typing():
        response = await get_chatbot_conversation(" ".join(args))
        bot_response = response.get('generated_text', None)
        if not bot_response:
            if 'error' in response:
                bot_response = '`Error: {}`'.format(response['error'])
            else:
                bot_response = 'Hmm... something is not right.'
    await ctx.send(bot_response)

# Playlist functions
# Add
@bot.command()
async def add(ctx, playlist, *songname):
    p = playlist.strip()
    s = " ".join(songname).strip()
    playlists.add_entry(p,s)
    await ctx.send(f"`Added {s} to {p}`")

# List
@bot.command()
async def list(ctx):
    await ctx.send(playlists.list_playlists())

# Songs
@bot.command()
async def songs(ctx):
    await ctx.send(playlists.list_songs())

# Playlist
@bot.command()
async def playlist(ctx, playlist):
    await ctx.send(playlists.list_songs_from_playlist(playlist))

# Get random songs
@bot.command()
async def play(ctx, *nsongs):
    if nsongs:
        await ctx.send(playlists.get_random_songs(nsongs[0]))
    else:
        await ctx.send(playlists.get_random_songs())

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    # Decorate the client with info about running chatbot
    client.active_chatbot = False

# This is only needed when we want to be parsing messages in channel
@client.event
async def on_message(message):

    # Skip parsing scrugbot message
    if message.author == client.user:
        return

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