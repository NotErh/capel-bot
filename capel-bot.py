#!/usr/bin/python3

# For this bot to work, create a text file called 'token_real.txt', place it in this script's directory, and paste your Discord bot token inside.
# For debug mode, use a text file called 'token_test.txt'

import discord
import asyncio

# argument parsing
import argparse
parser = argparse.ArgumentParser(description='Capel-bot v. 0.1.7. A simple Discord bot that provides various rot13 utilities.')
parser.add_argument('-d', '--debug',
                    nargs='?',
                    const=True,
                    help='Activate debug mode.')
parser.add_argument('--rotcount', help = "set the number of rot13's", type = int)
args = parser.parse_args()


# print discord.py version
print('\n\ndiscord.py version ' + str(discord.__version__))

# load other libraries
import sys
sys.path.insert(0, './plugins')
from rot_encoder import RotEncoder
from stats import Stats
from translate import GoogleTranslate

rot_encoder = RotEncoder()
stats = Stats()
translator = GoogleTranslate()

default_status_message = "PM me $help."

# debug mode from command flag
if args.debug == True:
    debug = True
    print("Starting in debug mode.")
else:
    debug = False
    print("Starting in normal (non-debug) mode.")

# manually set the rotcount if flag is present
if args.rotcount:
    print(args.rotcount)
    stats.set_rot_count(args.rotcount)

# finally start the client!
client = discord.Client(
    max_messages=20000, activity=discord.Game(name="%i ROT13's, dood!" % stats.get_rot_count() ))

# # # # # #
# Methods #
# # # # # #

# increase the rot13 count by one
async def increment_rot(client):
    stats.increment_rot()
    if stats.get_rot_count() == 1:
        await client.change_presence(activity=discord.Game(name="%i ROT13, dood!" % stats.get_rot_count()) )
    else:
        await client.change_presence(activity=discord.Game(name="%i ROT13's, dood!" % stats.get_rot_count() ))

# encode and send a rot13-encoded message (using an imbed)
async def encode_and_send_pm(message, client):
    e = create_embed(message)
    e.description = rot_encoder.encode_string(e.description)
    await message.author.send(embed = e)
    await increment_rot(client)

# method to create a quote embed object from a message
# most of this is from https://github.com/RalphORama/QuoteBot
def create_embed(message):
    # grab the author's color; if it doesn't exist, make it a default gray
    if hasattr(message.author, 'color'):
        author_color = message.author.color
    else:
        author_color = discord.Colour(0xFFFFFF)

    # create the embed object
    e = discord.Embed(description = message.content, color = author_color)
    e.set_author(name = message.author.display_name, icon_url = message.author.avatar_url_as(size=128))

    # source of the quote
    if isinstance(message.channel, discord.DMChannel):
        e.set_footer(text = "Private Message")
    else:
        e.set_footer(text = f"#{message.channel.name}")

    return e

# send a plaintext rot13's DM from a message
async def encode_and_send_plaintext_pm(message, client):
    text = rot_encoder.encode_string(message.content)
    await message.author.send(text)
    await increment_rot(client)


# help message
async def send_help_pm(message):
    text = ("```Hey! Thanks for using this bot and making life a bit easier for all of us who don't want to play spoiler Minesweeper.\n\n"
    "To ROT13 a message, simply send me a PM, and I'll spit the encoded/decoded message back at you.\n"
    "Alternatively, you can get the ROT13 of a message by reacting to it with :mag: or :mag_right: (the former looks nicer, the latter is in plaintext for easy copy/pasting)."
    "(this only works on the last 20,000 messages sent since the last Capel-bot restart, though)\n\n"
    "Happy spoilering!\n\n"
    "Update: You can now translate text into English or Japanese!\n"
    "Simply react with :hamburger: for an English translation, or with :sushi: for a Japanese translation.\n\n"
    "I sushi you all```")
    await message.channel.send(text)

# when receiving a PM, send a help message or rot13 the message
async def process_pm(message):
    # only react on non-bot messages
    if (message.author != client.user):
        # help
        if message.content.rstrip() == '$help':
            await send_help_pm(message)
        # or rot13
        else:
            await encode_and_send_plaintext_pm(message, client)

async def process_reaction_add(reaction, user):
    # if it's in a DMChannel (PM), if a :mag: emoji was added, try to return a copy-paste friendly version of the embed
    if isinstance(reaction.message.channel, discord.DMChannel):
        pass
    # reaction is added, check to see if it's the rot13 reaction emoji
    elif str(reaction) == u"\U0001F50D":
        e = create_embed(reaction.message)
        e.description = rot_encoder.encode_string(e.description)
        await user.send(embed = e)
        await increment_rot(client)
    # on :mag_right: emoji, send a PM with copy-paste friendly text
    elif str(reaction) == u"\U0001F50E":
        to_send = rot_encoder.encode_string(reaction.message.content)
        await user.send(to_send)
        await increment_rot(client)
    # flag reactions
    elif str(reaction) == u"\U0001F363":
        if u"\U0001F363" not in reaction.message.reactions:
            e = create_embed(reaction.message)
            t = translator.translate_to_ja(reaction.message.content)
            e.description = t.text
            e.set_footer(text = "Translated from %s" % t.src)
            await reaction.message.channel.send(embed = e)
    elif str(reaction) == u"\U0001F354":
        if u"\U0001F354" not in reaction.message.reactions:
            e = create_embed(reaction.message)
            t = translator.translate_to_en(reaction.message.content)
            e.description = t.text
            e.set_footer(text = "Translated from %s" % t.src)
            await reaction.message.channel.send(embed = e)

# respond to a message with a formatted list of emoji names and id's
async def list_guild_emoji(message):
    string = '```'
    for e in message.guild.emojis:
        string = string + str(e) + '\n'
    string = string + '```'
    await message.channel.send(string)
    
# respond to a message with a formatted list of emoji names
async def list_guild_emoji_name(message):
    string = '```'
    for e in message.guild.emojis:
        string = string + e.name + '\n'
    string = string + '```'
    await message.channel.send(string)



# Ready for the bot to make its appearance!
@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print("ID:", client.user.id)
    print('------')


# # # # # #
# Events  #
# # # # # #

# messages!
@client.event
async def on_message(message):
    # if the message is a PM (in a DMChannel)
    if (isinstance(message.channel, discord.DMChannel)):
        await process_pm(message)

# reactions
@client.event            
async def on_reaction_add(reaction, user):
    await process_reaction_add(reaction, user)



# use the test token if debugging, otherwise use the real token
if debug == True:
    token_file = 'token_test.txt'
else:
    token_file = 'token_real.txt'

# open token.txt
with open(token_file, 'r') as f:
    token = f.readline()
    token = token.strip()

# run the client
client.run(token)
    
