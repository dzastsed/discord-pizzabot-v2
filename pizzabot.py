import discord, asyncio, random, os, os.path, sys, aiomysql
from discord.ext import commands
from pymysql.converters import escape_string
from discord.ext.commands import bot_has_permissions
from dotenv import load_dotenv
from datetime import datetime
#from discord_slash import SlashCommand

#now = datetime.now()
#dtstring = now.strftime("[%Y-%m-%d %H:%M:%S]")

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
guild_ids =
whitelist_ids = []

def escape(s):
    if isinstance(s, str):
        return '\'{}\''.format(escape_string(s))
    return escape(str(s))

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
#slash = SlashCommand(bot, sync_commands=True)

async def initSql():
    global pool
    pool = await aiomysql.create_pool(
            host='127.0.0.1',
            port=3306,
            user='',
            password='',
            db='pizzabot',
            charset='utf8mb4',
            loop=asyncio.get_event_loop()
            )

async def closeSql():
    global pool
    pool.close()
    await pool.wait_closed()

initDone = False

@bot.event
async def on_ready():
    now = datetime.now()
    dtstring = now.strftime("[%Y-%m-%d %H:%M:%S]")
    global initDone
    print(dtstring, 'Logged in as {}#{}'.format(bot.user.name, bot.user.discriminator))
    await initSql()
    #await migrate() #uncomment if you want to migrate from v1, it took around 15 hours for 200k messages to migrate on my machine
    initDone = True
    print(dtstring, 'Loaded')

async def mysqlQuery(q):
    global pool
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(q)
            if q.upper().startswith('SELECT'):
                return await cur.fetchall()
            else:
                return await conn.commit()

async def logMessage(channel, text):
    now = datetime.now()
    dtstring = now.strftime("[%Y-%m-%d %H:%M:%S]")
    if text == '':
        return
    
    if text.startswith("--"):
        return
        
    print(dtstring, 'Logging a message in channel {}...'.format(channel))
    last = await mysqlQuery('''SELECT content FROM messages
                                WHERE channel='{}'
                                ORDER BY id desc
                                LIMIT 1'''
                            .format(channel)
                        )
    if len(last) != 0:
        content, = last[0]
    else:
        content = ''
    if len(last) == 0:
        await mysqlQuery('''INSERT INTO messages(content, channel, previousWord, secondLastWord) VALUES({}, '{}', '', '')'''.format(escape(text), channel))
    elif len(content) > 0:
        last = content.split(' ')
        await mysqlQuery('''INSERT INTO messages(content, channel, previousWord, secondLastWord)
                            VALUES({}, '{}', {}, {})'''
                        .format(
                            escape(text),
                            channel,
                            escape(last[-1].lower()),
                            escape(last[-2].lower() if len(last) > 1 else '')
                        )
                    )

    arr = text.split(' ')

    for i in range(len(arr)-1):
        await mysqlQuery('''INSERT INTO words(word, previousWord)
                            VALUES({}, {})'''
                        .format(
                            escape(arr[i+1]),
                            escape(arr[i].lower())
                        )
                    )
    print(dtstring, 'Logged!!')

@bot.event
async def on_message(msg):
   # now = datetime.now()
   # dtstring = now.strftime("[%Y-%m-%d %H:%M:%S]")
    global initDone
    if msg.author.bot or not initDone:
        return
    #return

    message = msg.clean_content

    if message.startswith("--"):
        return

    await logMessage(msg.channel.id, message)

    if isWhitelisted(msg):     
        if bot_has_permissions(send_messages=True):
            async with msg.channel.typing():
                msgArray = message.split()
        
                try:
                    startWord = await mysqlQuery('''SELECT content FROM messages WHERE previousWord = {0}
                                    UNION ALL SELECT content FROM messages WHERE previousWord = {0} AND secondLastWord = {1}
                                    UNION ALL SELECT content FROM messages WHERE previousWord = {0} AND secondLastWord = {1}
                                    ORDER BY rand() LIMIT 1'''
                                    .format(
                                        escape(msgArray[-1].lower()),
                                        escape(msgArray[-2].lower() if len(msgArray) > 1 else ' ') #word cant be a space because we split by space
                                    )
                                )
                    if len(startWord) < 1:
                        now = datetime.now()
                        dtstring = now.strftime("[%Y-%m-%d %H:%M:%S]")                                                
                        print(dtstring, 'start word not found')
                        raise Exception(dtstring, 'couldnt find a word')
                    now = datetime.now()
                    dtstring = now.strftime("[%Y-%m-%d %H:%M:%S]")
                    print(dtstring, 'Start word found')
                    content, = startWord[0]
                    startWord = content.split(' ')[0]
                    msgLen = random.randint(1, 10)
                    message = [startWord]
                    word = startWord
                    for i in range(msgLen):
                        word = await mysqlQuery('''SELECT word FROM words
                                        WHERE previousWord={}
                                        ORDER BY rand()
                                        LIMIT 1'''
                                    .format(
                                        escape(word.lower())
                                    )
                                )
                        if len(word) == 0:
                            break
                        word, = word[0]
                        message.append(word)
                        now = datetime.now()
                        dtstring = now.strftime("[%Y-%m-%d %H:%M:%S]")                        
                        print(dtstring, 'next word appended')
                    message = ' '.join(message)
                    if message != '':
                        await msg.channel.send(message)
                        return
                except:
                    pass
                #await msg.channel.send('no u')

async def migrate():
    files = [f for f in os.listdir('.') if os.path.isfile(os.path.join('.', f)) and f.endswith('.txt')]
    data = ''
    for fn in files:
        with open(fn, 'rb') as f:
            for e in f.read().decode('utf-8').split('\n'):
                try:
                    await logMessage(fn[:-4], e)
                except:
                    pass

#@slash.slash(name="restart", guild_ids=guild_ids, description="restart pizzasad if it doesnt work")
#async def restart(ctx):
#  embed=discord.Embed(title=":white_check_mark:",desc="Successfully Restarted")
#  await ctx.send("yo momma gay")
#  os.system("clear")
#  os.execv(sys.executable, ['python'] + sys.argv)
#  await ctx.send("succesfully restarted")

def isWhitelisted(msg):
    for id in whitelist_ids:
        if id == msg.channel.id:
            return True     
    return False
      
bot.run(TOKEN)
