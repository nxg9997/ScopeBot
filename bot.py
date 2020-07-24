# Perm Int: 3406912
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

keywords = {
    ""
}

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

    if random.randint(0,100) <= 10:
        await msg.channel.send('**- SCOPE -**')

print('Bot online')
client.run(token)