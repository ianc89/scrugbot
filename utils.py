import json
import requests
import re

def get_word():
    # Get a 5 letter word
    response = requests.get("https://random-word-api.herokuapp.com/word?number=15")
    json_data = json.loads(response.text)
    for x in json_data:
        if len(x) == 5:
            return x
    return get_word()

async def read_history(client, wordledb, wordle_match):
    # Reinitialise file
    wordledb.rebuild()
    # Channel ID
    og_id = 775730957985906718
    channel = client.get_channel(og_id)
    print (f"Parsing {channel}")
    # Get all history
    messages = await channel.history(limit=1000).flatten()
    # Write messages
    for m in messages:
        x = wordle_match.match(m.content)
        if x:
            wordledb.write([m.id,m.created_at, m.author.display_name, x.groups()[0],x.groups()[1],x.groups()[2]])
    
def get_emoji_numbers(text):
    # Function to get emoji numbers
    # Just have a mapping

    emoji_list =["1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","0️⃣"]
    emoji_real = [1,2,3,4,5,6,7,8,9,0]

    found_emoji = []
    for emoji, real in zip(emoji_list, emoji_real):
        if emoji in text:
            found_emoji.append(real)

    return found_emoji