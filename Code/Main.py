import youtube_dl
import discord
import emoji
import json
import os
import time
import discord.ext
import random
import asyncio
from flask_file import keep_alive
from discord.utils import get
from discord.ext import commands, tasks
from discord.ext.commands import has_permissions,  CheckFailure, check
# Use For A Cooldown On A Certain Command: ↓↓↓
#@commands.cooldown(1, 10, commands.BucketType.user)
#@commands.has_role("Admin") only admin can use
client = commands.Bot(command_prefix = '~') 
client.remove_command("help") # Removes The Default Help Command

# Variables
#   |
#   |
#   V

JOBS = {"cleaner":50, "streamer":200, "gamer":150, "cheff":300, "programmer":200}

EMOJIS = ["😀", "😁"]

FOODS = {"circle fruit" : 15, "triangle fruit" : 30, "square fruit" : 40, "star fruit" : 65, "small mushroom" : 10, "big mushroom" : 20, "watermelon" : 20, "bread" : 20, "lemon" : 20}

FOODS_UP = {"Circle fruit":":green_circle:", "Triangle fruit":":small_red_triangle:", "Square fruit":":purple_square:", "Star fruit":":star:", "Small mushroom":":mushroom:", "Big mushroom":":mushroom:", "Watermelon":":watermelon:", "Bread":":bread:", "Lemon":":lemon:"}

# Colours
c = 0x65aada

# Command Errors
#     |
#     |
#     V

@client.event
async def on_command_error(ctx, error):
	if isinstance(error, commands.MissingRequiredArgument):
		auto = discord.Embed(title = "Missing Arguments", description = 'Your command is missing arguments', color = discord.Color.red())
		await ctx.send(embed=auto)
	elif isinstance(error, commands.MissingRole):
		auto = discord.Embed(title = "Missing Role", description = "You don't have the role to use this command", color = discord.Color.red())
		await ctx.send(embed=auto)
	elif isinstance(error, commands.MissingPermissions):
		auto = discord.Embed(title = "Missing Permission", description = "You don't have the permission to use this command", color = discord.Color.red())
		await ctx.send(embed=auto)
	elif isinstance(error, commands.CommandNotFound):
		auto = discord.Embed(title = "Unknown Command", description = f'No such command "{ctx.message.content.replace("!", "")}" found', color = discord.Color.red())
		await ctx.send(embed=auto)
	elif isinstance(error, commands.CommandOnCooldown):
		auto = discord.Embed(title = "Command On Cooldown", description = "The command is on cooldown", color = discord.Color.red())
		await ctx.send(embed=auto)
	elif isinstance(error, commands.RoleNotFound):
		auto = discord.Embed(title = "Role Not Found", description = "Could not find the role", color = discord.Color.red())
		await ctx.send(embed=auto)
	elif isinstance(error, commands.MissingAnyRole):
		auto = discord.Embed(title = "Missing role", description = "You don't have the role to use this command", color = discord.Color.red())
		await ctx.send(embed=auto)
	else:
		print(error)


# Events
#   |
#   |
#   V

# On reaction Add

@client.event
async def on_reaction_add(reaction, member):
	print(reaction.emoji)
	print(reaction.message.content)
	print(str(reaction.emoji))
	for i in EMOJIS:
		print(str(reaction.emoji)==str(i))
	data = await get_game()
	msg_id = str(reaction.message.id)
	if msg_id in data:
		if data[msg_id]["completed"] == 0:
			await reaction.message.channel.send("You have not completed the game yet!")
			return
		if str(reaction.emoji) != str(data[msg_id]["emoji"]):
			await reaction.message.channel.send("Thats not the right emoji!")
			return
		await reward_member(member)
		del data[msg_id]
		await dump_game(data)

# Muted users cant speak when new channel is created 

@client.event
async def on_guild_channel_create(channel):
	Muted = get(channel.guild.roles, name='Muted')
	await channel.set_permissions(Muted, speak=False, send_messages=False)

# When a new user joins

@client.event
async def on_member_join(member):
	if not member.bot:
		role = get(member.guild.roles, name='Members')
		await member.add_roles(role)
	else:
		role = get(member.guild.roles, name='Bot')
		await member.add_roles(role)


# When Bot Starts Up

@client.event
async def on_ready():
    print("SlothyBot is Online") 

# Commands
#   |
#   |
#   V



# Moderation
#     |
#     V


# Ban
@client.command(aliases=["permkick","fullkick","permban","BAN","PERMBAN","PERMKICK","FULLKICK"])
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
  await member.ban(reason=reason)
  embed=discord.Embed(title="Banned!",description=f'{member} has been banned from the server',color=c)
  await ctx.send(embed=embed)
  
# Unban
@client.command(aliases=["unkick","unpermkick","unfullkick","UNKICK","UNPERMKICK","UNFULLKICK"])
@commands.has_permissions(ban_members=True)
async def unban(ctx, member, *, reason=None):
	banned_users = await ctx.guild.bans()
	try:
		member_name, member_disc = member.split('#')
	except:
		auto = discord.Embed(title = "Invalid argument", description = 'The argument yo passed was invalid', color = discord.Color.red())
		await ctx.send(embed=auto)
		return

	for ban in banned_users:
		user = ban.user

		if (user.name, user.discriminator) == (member_name, member_disc):
				await ctx.guild.unban(user)
				auto_guild = discord.Embed(title = 'Unban', description = f'{ctx.author.mention} unbanned {user.mention}', color = discord.Color.green())
				await ctx.send(embed=auto_guild)
				return
	auto_guild = discord.Embed(title = 'Unban', description = f'Could not find the ban', color = discord.Color.red())
	await ctx.send(embed=auto_guild)

# Kick
@client.command(aliases=["KICK"])
@commands.has_permissions()
async def kick(ctx, member: discord.Member, *, reason=None):
  await member.kick(reason=reason)
  if reason == None:
    await ctx.send(f'{member} has been kicked from the server for an unspecified reason.')
    return

  await ctx.send(f'{member} has been kicked from the server for {reason}.')

# Warn
@client.command(aliases=["WARN"])
@commands.has_permissions(kick_members=True)
async def warn(ctx, member : discord.Member):
	await open_warn(member)
	warnings = await warn_member(member)
	await ctx.send(f"warned {member.mention} user has {warnings} warnings")

# Delwarn
@client.command(aliases=["delwarn","delwarns","DELWARN","DELWARNS"])
@commands.has_permissions(kick_members=True)
async def unwarn(ctx, member : discord.Member, amount):
	await open_warn(member)
	warnings = await unwarn_member(member, amount)
	await ctx.send(f"cleared {amount} warnings {member.mention} user has {warnings} warnings")

# See Warns
@client.command(aliases=["seewarns","seewarn","warnings","infractions","howmanywarns","SEEWARNS","SEEWARN","WARNINGS","INFRACTIONS","HOWMANYWARNS"])
@commands.has_permissions(kick_members=True)
async def warns(ctx,  member : discord.Member):
	await open_warn(member)
	warnings = await show_warnings(member)
	await ctx.send(f"User {member.mention} has {warnings} warnings")

@client.command(aliases=["tempmute","shutup","TEMPMUTE","SHUTUP"])
@commands.has_permissions(kick_members=True)
async def mute(ctx,member : discord.Member,reason="no reason",time_=None):
	if time_:
		try:
			seconds = time_[:-1]
			duration = time_[-1]
			if duration == "s":
				seconds = seconds * 1
			elif duration == "m":
				seconds = seconds * 60
			elif duration == "h":
				seconds = seconds * 60 * 60
			elif duration == "d":
				seconds = seconds * 86400
			else:
				auto = discord.Embed(description = ":negative_squared_cross_mark: **Invalid duration input**", color = discord.Color.red())
				await ctx.send(embed=auto)
				return
			seconds = int(seconds)
		except Exception as e:
			print(e)
			auto = discord.Embed(description = ":negative_squared_cross_mark: **Invalid time input**", color = discord.Color.red())
			await ctx.send(embed=auto)
			return
	server = ctx.guild
	Muted = get(server.roles, name='Muted')


	if not Muted:
		Muted = await server.create_role(name='Muted')

		for channel in server.channels:
			await channel.set_permissions(Muted, speak=False, send_messages=False)

	for i in member.roles:
		if i.name == 'Full Muted':
			await member.remove_roles(i)

	await member.add_roles(Muted, reason=f"{ctx.author}: {reason}")
	auto = discord.Embed(description = f':white_check_mark: **{ctx.author} muted {member}**', color = c)

	await ctx.send(embed=auto)
	if time_:
		await asyncio.sleep(int(seconds))
		for i in member.roles:
			if i.name == 'Muted':
				await member.remove_roles(i)
				viesti = discord.Embed(description = f':white_check_mark: **User {member} has been unmuted**', color = c)
				await ctx.send(embed=viesti)


# Other Commands
#      |
#      V

# Reaction Roles
@client.command()
@commands.has_permissions(administrator=True, manage_roles=True)
async def reactrole(ctx, emoji, role: discord.Role, *, message):

    emb = discord.Embed(description=message)
    msg = await ctx.channel.send(embed=emb)
    await msg.add_reaction(emoji)

    with open('reactrole.json') as json_file:
        data = json.load(json_file)

        new_react_role = {'role_name': role.name, 
        'role_id': role.id,
        'emoji': emoji,
        'message_id': msg.id}

        data.append(new_react_role)

    with open('reactrole.json', 'w') as f:
        json.dump(data, f, indent=4)


@client.event
async def on_raw_reaction_add(payload):

    if payload.member.bot:
        pass

    else:
        with open('reactrole.json') as react_file:
            data = json.load(react_file)
            for x in data:
                if x['emoji'] == payload.emoji.name:
                    role = discord.utils.get(client.get_guild(
                        payload.guild_id).roles, id=x['role_id'])

                    await payload.member.add_roles(role)


@client.event
async def on_raw_reaction_remove(payload):

    with open('reactrole.json') as react_file:
        data = json.load(react_file)
        for x in data:
            if x['emoji'] == payload.emoji.name:
                role = discord.utils.get(client.get_guild(
                    payload.guild_id).roles, id=x['role_id'])

                
                await client.get_guild(payload.guild_id).get_member(payload.user_id).remove_roles(role)



# Poll
@client.command()
async def poll(ctx,*,message):
    emb=discord.Embed(title=" Poll:", description=f"{message}", color = c)
    msg=await ctx.channel.send(embed=emb)
    await msg.add_reaction('👍')
    await msg.add_reaction('👎')

# Ping
@client.command(aliases=["pingpong","PING","PINGPONG"])
async def ping(ctx):
		embed=discord.Embed(title="Pong!",color=c)
		await ctx.send(embed=embed)

# Help
@client.command(aliases=["helpme","HELP","HELPME"])
async def help(ctx):
  embed=discord.Embed(title="Click For Help", url="https://bit.ly/SlothyCmds", description="Click the blue text shown above to be shown a list of commands.", color=c)
  await ctx.send(embed=embed)
# Website
@client.command(aliases=["site","WEBSITE","SITE"])
async def website(ctx):
  embed=discord.Embed(title="Click For Website", url="https://bit.ly/SlothyBot", description="Click the blue text shown above to be shown the SlothyBot Website.", color=c)
  await ctx.send(embed=embed)

# Music Commands
#      |
#      |
#      V

#Play



@client.command()
async def play(ctx, url : str):
  song_there = os.path.isfile("song.mp3")
  try:
    if song_there:
      os.remove("song.mp3")
  except PermissionError:
    await ctx.send("Wait for the current music to end or use the '!leave' command")
  try:
    channel = ctx.author.voice.channel
  except AttributeError:
    embed=discord.Embed(title="Error:", description="You are not in a Voice Channel.", color=c)
    await ctx.send(embed=embed)
    return

  await channel.connect()

  embed=discord.Embed(title="Success:", description="The bot is now playing the audio!", color=c)
  await ctx.send(embed=embed)
  voice = discord.utils.get(client.voice_clients, guild=ctx.guild)

  ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
      'key': 'FFmpegExtractAudio',
      'preferredcodec': 'mp3',
    }]
  }
  with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    ydl.download([url])
  for file in os.listdir("./"):
    if file.endswith(".mp3"):
      os.rename(file, "song.mp3")
  voice.play(discord.FFmpegPCMAudio("song.mp3"))





#Leave

@client.command(aliases=["leave","LEAVE"])
async def disconnect(ctx):
  voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
  if not voice:
    embed=discord.Embed(title="Error:", description="The bot is not connected to a Voice Channel.", color=c)
    await ctx.send(embed=embed)
  if voice.is_connected():
    await voice.disconnect()
    embed=discord.Embed(title="Success:", description="The bot has left the Voice Channel.", color=c)
    await ctx.send(embed=embed)

#Pause

@client.command()
async def pause(ctx):
  voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
  if not voice:
    embed=discord.Embed(title="Error:", description="There is no audio playing.", color=c)
    await ctx.send(embed=embed)
  if voice.is_playing():
    voice.pause()
    embed=discord.Embed(title="Success:", description="Audio paused.", color=c)
    await ctx.send(embed=embed)

#Resume

@client.command(aliases=["unpause"])
async def resume(ctx):
  voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
  if not voice:
    embed=discord.Embed(title="Error:", description="The audio is not paused.", color=c)
    await ctx.send(embed=embed)
  if voice.is_paused():
    voice.resume()
    embed=discord.Embed(title="Success:", description="Audio resumed.", color=c)
    await ctx.send(embed=embed)

# Economy
#   |
#   |
#   V

#Balance
@client.command(aliases=["bal","money","BALANCE","BAL","MONEY"])
async def balance(ctx, member:discord.Member = None):
	if not member:
		member = ctx.author
	await open_account(member)
	wallet_balance, bank_balance = await show_balance(member)
	embed=discord.Embed(title="Money:", description=f"⏣{wallet_balance} in the wallet and ⏣{bank_balance} in the bank.", color=c)
	await ctx.send(embed=embed)


#Send money
@client.command()
async def send(ctx, member: discord.Member, amount):
	amount = int(amount)
	await open_account(ctx.author)
	m_id = str(member.id)
	a_id = str(ctx.author.id)
	await open_account(member)
	data = await get_bank()
	wallet, bank = await show_balance(ctx.author)
	if wallet < amount:
		await ctx.send("you dont have enough money")
		return
	data[a_id]["wallet"] -= amount
	data[m_id]["wallet"] += amount
	await dump_bank(data)
	await ctx.send("succesfully sent money")



# Find Money
@client.command(aliases=["coinsearch","free","freemoney","COINSEARCH","FREE","FREEMONEY"])
@commands.cooldown(1, 10, commands.BucketType.user)
async def find(ctx):
	await open_account(ctx.author)
	amount = await find_money(ctx.author)
	wallet_balance, bank_balance = await show_balance(ctx.author)
	await ctx.send(f"You got ⏣{amount} of money! You now have ⏣{wallet_balance} in your wallet!")

#Gamble Money
@client.command(aliases=["GAMBLE"])
async def gamble(ctx, amount):
	await open_account(ctx.author)
	wallet_balance, bank_balance = await show_balance(ctx.author)
	try:
		amount = int(amount)
	except ValueError:
		embed=discord.Embed(title="Error:", description=f"Invalid Amount. Try putting in a number not a word or symbol", color=c)
		await ctx.send(embed=embed)
		return

	if amount < 69:
		embed=discord.Embed(title="Error:", description=f"Invalid Amount. Minimum bet is ⏣69", color=c)
		await ctx.send(embed=embed)
		return
	
	if wallet_balance < amount:
		embed=discord.Embed(title="Error:", description=f"You have less than ⏣{amount} in your wallet. Try withdrawing some money from your bank then try again. You have ⏣{wallet_balance} and ⏣{bank_balance} in your bank.", color=c)
		await ctx.send(embed=embed)
		return

	
	result, given_amount = await gamble_money(ctx.author, amount)
	wallet_balance, bank_balance = await show_balance(ctx.author)
	if result == 1:
		winemb=discord.Embed(title="Win!", description=f"You got ⏣{given_amount}! You now have ⏣{wallet_balance} in your wallet!", color=c)    
		await ctx.send(embed=winemb)
	elif result == 0.5:
		tieemb=discord.Embed(title="TIE!", description=f"You got ⏣{given_amount}! You now have ⏣{wallet_balance} in your wallet!", color=c)
		await ctx.send(embed=tieemb)
	elif result == 0:
		lossemb=discord.Embed(title="Loss :(", description=f"You lost ⏣{amount}! You now have ⏣{wallet_balance} in your wallet!", color=c)
		await ctx.send(embed=lossemb)


# Deposit command
@client.command(aliases=["givebank","bankgive","DEPOSIT","GIVEBANK","BANKGIVE"])
async def deposit(ctx, amount):
	await open_account(ctx.author)
	wallet_balance, bank_balance = await show_balance(ctx.author)
	try:
		amount = int(amount)
	except ValueError:
		embed=discord.Embed(title="Error:", description=f"Invalid Amount. Try putting in a number not a word or symbol", color=c)
		await ctx.send(embed=embed)
		return

	if wallet_balance < amount:
		embed=discord.Embed(title="Error:", description=f"You have less than ⏣{amount} in your wallet. Try withdrawing some money from your bank then try again. You have ⏣{wallet_balance} and ⏣{bank_balance} in your bank.", color=c)
		await ctx.send(embed=embed)
		return

	await deposit_money(ctx.author, amount)
	wallet_balance, bank_balance = await show_balance(ctx.author)
	await ctx.send(f"You now have ⏣{wallet_balance} in your wallet and ⏣{bank_balance} in your bank")

# Withdraw
@client.command(aliases=["takebank","banktake","take","WITHDRAW","TAKEBANK","BANKTAKE","TAKE"])
async def withdraw(ctx, amount):
	await open_account(ctx.author)
	wallet_balance, bank_balance = await show_balance(ctx.author)
	try:
		amount = int(amount)
	except ValueError:
		embed=discord.Embed(title="Error:", description=f"Invalid Amount, Try putting in a number not a word ", color=c)
		await ctx.send(embed=embed)
		return

	if bank_balance < amount:
		embed=discord.Embed(title="Error:", description=f"You have less than ⏣{amount} in your bank. You have ⏣{wallet_balance} and ⏣{bank_balance} in your bank.", color=c)
		await ctx.send(embed=embed)
		return

	await withdraw_money(ctx.author, amount)
	wallet_balance, bank_balance = await show_balance(ctx.author)
	await ctx.send(f"You now have ⏣{wallet_balance} in your wallet and ⏣{bank_balance} in your bank")

@client.command(aliases=["seeshop","SHOP","SEESHOP"])
async def shop(ctx):
		
	viesti = discord.Embed(title = "Pet Point Shop", description = f"Here you can buy food for your pet", color = c)
	viesti.add_field(name="Watermelon :watermelon:", value="""
	70 happiness boost
	⏣**150**
	""")
	viesti.add_field(name="Bread :bread:", value="""
	70 happiness boost
	**⏣150**
	""")
	viesti.add_field(name="Lemon :lemon:", value="""
	70 happiness boost
	⏣**150**
	""")
	viesti.set_thumbnail(url="https://www.cuteeasydrawings.com/uploads/allimg/200622/1-2006220R6110-L.jpg")
	await ctx.send(embed=viesti)

@client.command(aliases=["purchase","BUY","PURCHASE"])
async def buy(ctx, item, amount):
	await open_account(ctx.author)
	amount = int(amount)
	item_fix = item.lower()
	if item_fix not in FOODS.keys():
		viesti = discord.Embed(description = f"You succesfully bought **{item_fix}**", color = 0xFFFFFF)
		await ctx.send(embed=viesti)
		return
	cost_single = FOODS[item_fix]
	cost = cost_single * amount
	wallet_balance, bank_balance = await show_balance(ctx.author)

		
	if wallet_balance >= cost:
		data = await get_bank()
		m_id = str(ctx.author.id)
		data[m_id]["wallet"] -= cost
		if item_fix not in data[m_id]["inventory"]:
			data[m_id]["inventory"][item_fix] = amount
		else:
			data[m_id]["inventory"][item_fix] += amount
		await dump_bank(data)
		viesti = discord.Embed(description = f"You succesfully bought **{amount}** **{item_fix}**", color = c)
		await ctx.send(embed=viesti)
		return
	else:
		viesti = discord.Embed(description = f"Uh oh, you don't have enough points.", color = c)
		await ctx.send(embed=viesti)
		return

@client.command(aliases=["inv","invsee","seeinv"])
async def inventory(ctx):
	await open_account(ctx.author)
	data = await get_bank()
	m_id = str(ctx.author.id)

	viesti = discord.Embed(title="Item Inventory", description = f"You can see your items here", color = c)
	index = 0
	for k, v in data[m_id]["inventory"].items():
		viesti.set_thumbnail(url="https://cdn.discordapp.com/attachments/900712260937322529/908763716743491584/inventory_apple.png")
		if v != 0:
			viesti.add_field(name=f"{k}", value=f"Amount : {v}")
			index += 1
	if index == 0:
		viesti.description = "You don't have any food!"

	await ctx.send(embed=viesti)

# WORK
#   |
#   |
#   V

@client.command(aliases=["quit","quitjob","RESIGN","QUIT","QUITJOB"])
async def resign(ctx):
	await open_account(ctx.author)
	a_id = str(ctx.author.id)
	data = await get_bank()
	if not data[a_id]["job"]:
		await ctx.send("You didnt have a job")
		return
	data[a_id]["job"] = None
	await dump_bank(data)
	await ctx.send("You resigned")

@client.command(aliases=["apply","getjob","JOB","APPLY","GETJOB"])
@commands.cooldown(1, 10, commands.BucketType.user)
async def job(ctx, job):
	await open_account(ctx.author)
	a_id = str(ctx.author.id)
	data = await get_bank()
	if data[a_id]["job"]:
		await ctx.send("You already have a job")
		return
	if job not in JOBS.keys():
		await ctx.send("Invalid job")
		return
	random_num = random.randint(1, 100)
	if random_num > 35:
		await ctx.send("You didnt get the job")
		return
	data[a_id]["job"] = job
	await dump_bank(data)
	await ctx.send("You got the job!")

@client.command()
async def work(ctx):
	await open_account(ctx.author)
	a_id = str(ctx.author.id)
	data = await get_bank()
	if not data[a_id]["job"]:
		await ctx.send("You dont have a job yet")
		return
	data = await get_game()
	auto = discord.Embed(title="Work", description = "You can do your ", color = discord.Color.red())
	msg = await ctx.send(embed=auto)
	msg_id = str(msg.id)
	data[msg_id] = {}
	data[msg_id]["completed"] = 0
	emj = random.choice(EMOJIS)
	print(emj)
	data[msg_id]["emoji"] = emj
	await dump_game(data)

  
# HELPER FUNCTION

async def reward_member(member):
	data = await get_bank()
	m_id = str(member.id)
	job = data[m_id]["job"]
	if not job:
		return False
	data[m_id]["wallet"] += JOBS[job]
	await dump_bank(data)

async def dump_game(data):
	with open("game_data.json", "w") as f:
		return json.dump(data, f, indent=4)

async def get_game():
	with open("game_data.json", "r") as f:
		return json.load(f)

async def dump_warnings(data):
	with open("warnings.json", "w") as f:
		return json.dump(data, f, indent=4)

async def get_warnings():
	with open("warnings.json", "r") as f:
		return json.load(f)

async def open_warn(member):
	data = await get_warnings()
	g_id = str(member.guild.id)
	m_id = str(member.id)
	if g_id in data and m_id in data[g_id]:
		return False
	else:
		if g_id not in data:
			data[g_id] = {}
		data[g_id][m_id] = 0

	await dump_warnings(data)


#Reads how much money the user has 
async def get_bank():
	with open('data.json', 'r') as f:
		users = json.load(f)
		return users

#Writes the new amount of money the user should have
async def dump_bank(data):
	with open('data.json', 'w') as f:
		json.dump(data,f, indent=4)

#Creates a bank account for the user
async def open_account(member):
	data = await get_bank()
	m_id = str(member.id)
	if m_id in data:
		return False
	data[m_id] = {}
	data[m_id]["wallet"] = 10
	data[m_id]["bank"] = 500
	data[m_id]["inventory"] = {}
	data[m_id]["job"] = None
	await dump_bank(data)

#Displays how much money the user has
async def show_balance(member):
	data = await get_bank()
	m_id = str(member.id)
	return data[m_id]["wallet"], data[m_id]["bank"]

#Function used for "!find", gets a random amount of money and gives to the user
async def find_money(member):
	data = await get_bank()
	amount = random.randint(5, 100)
	m_id = str(member.id)
	data[m_id]["wallet"] += amount
	await dump_bank(data)
	return amount
	
# Gamble helper function
async def gamble_money(member, amount):
	data = await get_bank()
	m_id = str(member.id)
	member_random_number = random.randint(1, 515)
	bot_random_number = random.randint(1, 565)

	if member_random_number < bot_random_number:
		multiplier = -1
		data[m_id]["wallet"] -= amount
		await dump_bank(data)
		return 0, int(amount * multiplier) * -1

	if member_random_number == bot_random_number:
		multiplier = 50
		data[m_id]["wallet"] += int(amount * multiplier)
		await dump_bank(data)
		return 0.5, int(amount * multiplier)
	
	if member_random_number > bot_random_number:
		multiplier = 1
		data[m_id]["wallet"] += int(amount * multiplier)
		await dump_bank(data)
		return 1, int(amount * multiplier)

# Deposit money into bank
async def deposit_money(member, amount):
	data = await get_bank()
	m_id = str(member.id)

	data[m_id]["bank"] += amount
	data[m_id]["wallet"] -= amount

	await dump_bank(data)

# Withdraw money from the bank
async def withdraw_money(member, amount):
	data = await get_bank()
	m_id = str(member.id)

	data[m_id]["bank"] -= amount
	data[m_id]["wallet"] += amount

	await dump_bank(data)

# Warn members
async def warn_member(member):
	data = await get_warnings()
	g_id = str(member.guild.id)
	m_id = str(member.id)

	data[g_id][m_id] += 1
	warnings = data[g_id][m_id]

	await dump_warnings(data)
	return warnings

# Delete Warnings
async def unwarn_member(member, amount):
	data = await get_warnings()
	g_id = str(member.guild.id)
	m_id = str(member.id)

	data[g_id][m_id] -= int(amount)
	data[g_id][m_id]
	if data[g_id][m_id] < 0:
		data[g_id][m_id] = 0

	await dump_warnings(data)
	return data[g_id][m_id]

async def show_warnings(member):
	data = await get_warnings()
	g_id = str(member.guild.id)
	m_id = str(member.id)
	return data[g_id][m_id]
  

# 


# Logs In The Bot
#     |
#     |
#     V
# KEEP AT BOTTOM

keep_alive()
client.run(os.getenv("TOKEN"))
 
