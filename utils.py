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

async def read_history(client, wordledb, wordle_match, quordle=False):
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
            if not quordle:
                wordledb.write([m.id,m.created_at, m.author.display_name, x.groups()[0],x.groups()[1],x.groups()[2]])
            else:
                results = get_emoji_numbers(m.content)
                total = sum(results)
                wordledb.write([m.id, m.created_at, m.author.display_name, x.groups()[0], x.groups()[1], total])
        
    
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

def get_wordle_results():
    import pandas
    df = pandas.read_csv("wordle.csv",header=None)
    # 0 - msg id, 1 - timestamp, 2 - username, 3 - Wordle, 4 - #wordle, 5 - result
    df = df.drop([0,1,3,4], axis=1)
    res = dict(df.value_counts())
    # get list of users and generate results
    users = {}
    for r in res:
        if r[0] not in users:
            users[r[0]] = ["1:","2:","3:","4:","5:","6:"]
        if r[1] == "1/6":
            users[r[0]][0] += "+"*res[r]
        elif r[1] == "2/6":
            users[r[0]][1] += "+"*res[r]
        elif r[1] == "3/6":
            users[r[0]][2] += "+"*res[r]
        elif r[1] == "4/6":
            users[r[0]][3] += "+"*res[r]
        elif r[1] == "5/6":
            users[r[0]][4] += "+"*res[r]
        elif r[1] == "6/6":
            users[r[0]][5] += "+"*res[r]

    # Now prepare message
    message = "\n"
    for user in users:
        message += "---- "+user+"\n```"
        for r in users[user]:
            message += r+"```\n"
    message += "\n"
    return message

def get_quordle_results():
    import pandas
    df = pandas.read_csv("quordle.csv",header=None)
    # 0 - msg id, 1 - timestamp, 2 - username, 3 - Wordle, 4 - #wordle, 5 - result
    df = df.drop([0,1,3,4], axis=1)
    res = dict(df.value_counts())
    # get list of users and generate results
    users = {}
    for r in res:
        if r[0] not in users:
            users[r[0]] = ["00-08:","08-16:","16-24:","24-32:","32+  :"]
        val = int(r[1])
        if val < 8:
            users[r[0]][0] += "+"*res[r]
        elif val < 16:
            users[r[0]][1] += "+"*res[r]
        elif val < 32:
            users[r[0]][2] += "+"*res[r]
        elif val < 36:
            users[r[0]][3] += "+"*res[r]
        else:
            users[r[0]][4] += "+"*res[r]

    # Now prepare message
    message = "\n"
    for user in users:
        message += "---- "+user+"\n```"
        for r in users[user]:
            message += r+"```\n"
    message += "\n"
    return message