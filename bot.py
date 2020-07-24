# Perm Int: 3406912
print('hello world')
import discord
import random

import os
token = ''
if os.environ.get('HOSTED') == None:
    import config
    token = config.token
else:
    token = str(os.environ.get('HOSTED'))
    print('Running on Heroku, token = ' + token)

scopebook = [
    "**- SCOPE -**",
    "*But have you considered... scope?*",
    "I like your idea, but, it's a little outside the scope 乁| ･ 〰 ･ |ㄏ",
    "https://pmweb.com/wordpress/wp-content/uploads/2017/12/Scope-blog-Joao.jpg"
]

client = discord.Client()

@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))

@client.event
async def on_message(msg):
    if msg.author == client.user:
        return
    if msg.content.startswith('$hello'):
        await msg.channel.send('Hello!')

    if msg.content.startswith('!scope'):
        await msg.channel.send(scopebook[random.randint(0,len(scopebook)-1)])
    elif random.randint(0,100) <= 10:
        await msg.channel.send(scopebook[random.randint(0,len(scopebook)-1)])

    

print('Bot online')
client.run(token)