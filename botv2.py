import os
import re
import discord
import dotenv
from utils import get_word, read_history, get_emoji_numbers, get_wordle_results, get_quordle_results, get_chatbot_conversation
from db import dbcsv
from music import playlists

# Using command decorators now
from discord.ext import commands

# Change only the no_category default string
help_command = commands.DefaultHelpCommand(
    no_category = 'Commands'
)

# Our bot operator
client = commands.Bot(
    command_prefix='.', 
    description="SCRUGBOT\nScrugbot will automatically store wordle and quordle results\n",
    help_command = help_command
    )

# Load .env file
dotenv.load_dotenv()

# Databases
wordledb  = dbcsv("wordle.csv")
quordldb  = dbcsv("quordle.csv")
playlists = playlists()

# Regex
wordle_match_str = r"(Wordle) (\d+) (\d+/\d+|X/\d+)"
wordle_match = re.compile(wordle_match_str)

quordle_match_str = r"(Daily Quordle) \#(\d+)"
quordle_match = re.compile(quordle_match_str)

# Greeting
@client.command(help="Say hello!")
async def hello(ctx):
    await ctx.send(f'Hello {ctx.message.author.display_name}!')

# Rebuild function
@client.command(help="Rebuild the word game databases")
async def rebuild(ctx):
    await ctx.send('Rebuilding results')
    await read_history(client, wordledb, wordle_match)
    await read_history(client, quordldb, quordle_match, True)
    await ctx.send('Finished rebuild request')

# Word function
@client.command(help="Get a 5 letter word suggestion")
async def word(ctx):
    await ctx.send(f"Why not try ... {get_word()}")

# Wordle results function
@client.command(help="Display wordle results")
async def wordle(ctx):
    await ctx.send(get_wordle_results())

# Quordle results function
@client.command(help="Display quordle results")
async def quordle(ctx):
    await ctx.send(get_quordle_results())

# Chatbot functions
# Turn on
@client.command(help="Turn on the Hagrid chatbot")
async def chat(ctx):
    client.active_chatbot = True
    await ctx.send("scrugbot is sentient")

# Turn off
@client.command(help="Turn off the Hagrid chatbot")
async def stop(ctx):
    client.active_chatbot = False
    await ctx.send("scrugbot is dumb")

# Ask
@client.command(help="Ask chatbot a question")
async def ask(ctx, *question):
    if not client.active_chatbot:
        return

    async with ctx.message.channel.typing():
        response = await get_chatbot_conversation(" ".join(question))
        bot_response = response.get('generated_text', None)
        if not bot_response:
            if 'error' in response:
                bot_response = '`Error: {}`'.format(response['error'])
            else:
                bot_response = 'Hmm... something is not right.'
    await ctx.send(bot_response)

# Playlist functions
# Add
@client.command(help="Add a song to the playlist")
async def add(ctx, playlist, *songname):
    p = playlist.strip()
    s = " ".join(songname).strip()
    playlists.add_entry(p,s)
    await ctx.send(f"`Added {s} to {p}`")

# List
@client.command(help="List all stored playlist names")
async def list(ctx):
    await ctx.send(playlists.list_playlists())

# Songs
@client.command(help="List all songs and playlists")
async def songs(ctx):
    async with ctx.message.channel.typing():
        songs = await playlists.list_songs()
    await ctx.send(songs)

# Playlist
@client.command(help="List all songs in a playlist")
async def playlist(ctx, playlist):
    await ctx.send(playlists.list_songs_from_playlist(playlist))

# Get random songs
@client.command(help="Get a random selection of songs from all playlists")
async def play(ctx, nsongs=10):
    if nsongs:
        await ctx.send(playlists.get_random_songs(nsongs))
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

    # Special - We override on_message, so need to add this to process custom commands
    await client.process_commands(message)

# If invalid command
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("**Invalid command. Try using** `help` **to figure out commands!**")
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('**Please pass in all requirements.**')
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("**You dont have all the requirements or permissions for using this command :angry:**")

# Run client
client.run(os.getenv('TOKEN'))