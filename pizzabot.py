import discord, asyncio, random, os, os.path, sys, aiomysql
from pymysql.converters import escape_string

def escape(s):
	if isinstance(s, str):
		return '\'{}\''.format(escape_string(s))
	return escape(str(s))

client = discord.Client()

async def initSql():
	global cur, conn
	conn = await aiomysql.connect(
			host='127.0.0.1',
			port=3306,
			user='root',
			password='',
			db='pizzabot',
			charset='utf8mb4',
			loop=asyncio.get_event_loop()
		   )
	cur = await conn.cursor()

async def closeSql():
	global cur, conn
	await cur.close()
	conn.close()

initDone = False

@client.event
async def on_ready():
	global initDone
	print('Logged in as {}#{}'.format(client.user.name, client.user.discriminator))
	await initSql()
  #await migrate() #uncomment if you want to migrate from v1, it took around 15 hours for 200k messages to migrate on my machine
	initDone = True
	print('Loaded')

async def mysqlQuery(q):
	global cur, conn
	await cur.execute(q)
	if q.upper().startswith('SELECT'):
		return await cur.fetchall()
	else:
		return await conn.commit()


async def logMessage(channel, text):
	if text == '':
		return
	print('Logging a message in channel {}...'.format(channel))
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
	print('Logged!!')

@client.event
async def on_message(msg):
	global initDone
	if msg.author.bot or not initDone:
		return
	#return
	
	message = msg.clean_content
	
	await logMessage(msg.channel.id, message)
	
	msgArray = message.split()
	try:
		m = await client.send_message(msg.channel, 'Please wait...')
	except:
		return
	
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
			print('start word not found')
			raise Exception('couldnt find a word')
		print('Start word found')
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
			print('next word appended')
		message = ' '.join(message)
		if message != '':
			await client.edit_message(m, message)
			return
	except:
		pass
	await client.edit_message(m, 'no u')

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

client.run('token')
