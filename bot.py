# Perm Int: 3406912

# Import Libraries / Modules
import discord
import random

import os

import mysql.connector

import numpy as np

# Only import Config.py if the bot is being run locally
# 'HOSTED' is a environment variable set on Heroku that equals the bot token
token = ''
sql_conn_info = {}
if os.environ.get('HOSTED') == None:
    import config
    token = config.token
    sql_conn_info = config.sql_data
else:
    token = str(os.environ.get('HOSTED'))
    #sqlurl = str(os.environ.get('JAWSDB_URL'))
    print('Running on Heroku, token = ' + token)
    sql_conn_info['host'] = str(os.environ.get('DB_HOST'))
    sql_conn_info['username'] = str(os.environ.get('DB_USER'))
    sql_conn_info['password'] = str(os.environ.get('DB_PASS'))
    sql_conn_info['database'] = str(os.environ.get('DB_DB'))
    sql_conn_info['port'] = str(os.environ.get('DB_PORT'))

import data

# create a Discord client instance
client = discord.Client()

# connect to MySQL
db_connection = mysql.connector.connect(
    host=sql_conn_info['host'],
    user=sql_conn_info['username'],
    passwd=sql_conn_info['password']
)


# Helper functions
def ReadCountFromDB(usr):
    db_cursor = db_connection.cursor()
    query = "select `count` from `" + sql_conn_info['database'] + "`.`Counter` where `user`='" + str(usr) + "' limit 1"
    #print(query)
    db_cursor.execute(query)
    found = False
    for db in db_cursor:
        found = True
        #print(db)
        return str(db[0])
    if not found:
        query = "insert into `" + sql_conn_info['database'] + "`.`Counter` (`user`) values ('" + str(usr) + "')"
        db_cursor.execute(query)
        db_connection.commit()
        #print(query)
        #print(db_cursor.Info())
        return "0"
    db_cursor.close()
    return "-1"

# Add user to scope counter OR increment their total
def IncrementUser(usr):
    result = int(ReadCountFromDB(usr))
    result = result + 1
    db_cursor = db_connection.cursor()
    query = "update `" + sql_conn_info['database'] + "`.`Counter` set `count` = " + str(result) + " where `user` = '" + str(usr) + "'"
    #print(query)
    db_cursor.execute(query)
    db_connection.commit()
    db_cursor.close()
    '''
    if not usr in data.scopecounter:
        data.scopecounter[usr] = 0
    data.scopecounter[usr] = data.scopecounter[usr] + 1
    '''

# Gets a string with the user's total number of out of scope ideas
def GetTotalString(usr):
    IncrementUser(usr)
    return "**<@" + str(usr) + "> has had " + ReadCountFromDB(usr) + " badly scoped idea(s)!**"

# Retrieves a quote, and will @ the user if supported by the quote
def GetQuote(usr):
    quote = data.scopebook[random.randint(0,len(data.scopebook)-1)]
    quote = quote.replace('$','<@' + str(usr) + '>')
    return quote

# Check if a message contains a keyword
def ContainsKeyword(msg):
    if any(map(msg.content.lower().__contains__,data.keywords)):
        return True
    
    return False

def Scoreboard():
    result = '```diff\nScoreboard\n=====\n'
    db_cursor = db_connection.cursor()
    query = "select * from `" + sql_conn_info['database'] + "`.`Counter`"
    #print(query)
    db_cursor.execute(query)
    size = 0
    db_res = []
    for db in db_cursor:
        size += 1
        db_res.append([db[0],db[1]])
    arr = np.zeros(shape=(size,2))
    #ptr = 0
    for x in range(len(db_res)):
        #print(db[0])
        arr[x, 0] = int(db_res[x][0])
        arr[x, 1] = int(db_res[x][1])
        #ptr += 1

    #arr[0,0] = 1
    db_cursor.close()
    print(arr)
    sortedArr = arr[arr[:,1].argsort()]

    print(sortedArr)
    for x in range(size):
        result += "<@" + str(f"{sortedArr[x][0]:8f}")[0:-7] + "> : " + str(sortedArr[x][1]) + '\n'
    return result




# Discord Events

# When the bot is successfully logged in
@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))

# When a message is sent to a channel visible to the bot
@client.event
async def on_message(msg):

    # enforces cooldown on sending scope messages
    if not str(msg.channel.id) in data.cooldowns:
        data.cooldowns[str(msg.channel.id)] = 0
    elif data.cooldowns[str(msg.channel.id)] > 0:
        data.cooldowns[str(msg.channel.id)] -= 1

    # ignore messages sent by the bot
    if msg.author == client.user:
        return
    
    # 'hello' ping
    if msg.content.startswith('$hello'):
        await msg.channel.send('Hello!')

    elif msg.content.startswith('!mycount'):
        count = ReadCountFromDB(msg.author.id)
        await msg.channel.send("<@" + str(msg.author.id) + "> **has had " + str(count) + " out-of-scope ideas!**")

        '''
        elif msg.content.startswith('!incme'):
            IncrementUser(msg.author.id)
            await msg.channel.send("done")
        '''
    # tells the user how many out-of-scope counts each mentioned user has
    elif msg.content.startswith('!countfor'):
        counts = []
        result = "**Out-of-scope count(s):"
        for mention in msg.mentions:
            #counts.append(ReadCountFromDB(mention.id))
            result = result + " <@" + str(mention.id) + "> has " + ReadCountFromDB(mention.id) + ","
        result = result[0:len(result) - 1] + "**"
        await msg.channel.send(result)
    elif msg.content.startswith('!scoreboard'):
        await msg.channel.send(Scoreboard())

    else:
        # send a scope reminder (by using a command, random chance, or by containing a keyword)
        if msg.content.startswith('!scope'):
            await msg.channel.send(GetQuote(msg.author.id))
        elif (random.randint(0,100) <= 5 or ContainsKeyword(msg)) and data.cooldowns[str(msg.channel.id)] == 0:
            data.cooldowns[str(msg.channel.id)] = 10

            await msg.channel.send(GetQuote(msg.author.id) + "\n" + GetTotalString(msg.author.id))

            # reserved spot for some dank memes
            '''
            if random.randint(0, 100) <= 42:
                await msg.channel.send(GetQuote(msg.author.id))
            else:
                await msg.channel.send(GetQuote(msg.author.id))
            '''

    
# run the bot
print('Bot online')
client.run(token)