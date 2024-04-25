import discord
import os

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents = intents)
channel = None
category = None

# Print a message when the bot is logged in.
@client.event
async def on_ready():
	print("%s is logged in!" % (client.user))

# This is a function decorator that decorates client's event function.
# on_message is decorated (reassigned) with client.event's return value.
@client.event
async def on_message(message):
	global category
	global channel

	# Ignore message if it was sent by the bot.
	if message.author == client.user:
		return

	# Ensure that sillybot is being used by an admin.
	if message.content.startswith("$"):
		if not message.channel.permissions_for(message.author).administrator:
			await message.channel.send("Sorry, you need to be an admin to use sillybot.")
			return

	# Command to set category.
	if message.content.startswith("$category"):
		argument = message.content.split(" ", 1)[1]
		category = discord.utils.get(message.channel.guild.categories, name = argument)
		if category is None:
			await message.channel.send("The category \"%s\" does not exist!" % argument)
			return

		await message.channel.send("The category is set to \"%s\"." % argument)

	# Command to set channel.
	if message.content.startswith("$channel"):
		argument = message.content.split(" ", 1)[1]
		channel = discord.utils.get(message.channel.guild.channels, name = argument)
		if channel is None:
			await message.channel.send("The channel \"%s\" does not exist!" % argument)
			return

		await message.channel.send("The channel was set to \"%s\"." % argument)

	# Repost into the given channel if a message was sent anywhere in a category. 
	if category is not None and channel is not None and message.channel.category == category:
		images = []
		for attachment in message.attachments:
			images.append(await attachment.to_file())

		repost = await channel.send(content = "%s:\n%s" % (message.jump_url, message.content), files = images)
		await repost.edit(suppress = True)

client.run(os.environ["TOKEN"])
