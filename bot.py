# Perm Int: 3406912
import discord
import random
import config

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

client.run(config.token)