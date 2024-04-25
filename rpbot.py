import discord
import os

class rpbot(discord.Client):
	# Array of server handlers.
	handlers = dict()

	def __init__(self, intents):
		super().__init__(intents = intents)

	async def on_ready(self):
		print("%s is logged in!" % (client.user))

	async def on_message(self, message):
		if not message.guild.id in self.handlers:
			self.handlers[message.guild.id] = server_handler(message.guild)

		await self.handlers[message.guild.id].process_message(message)

class server_handler:
	server = None
	category = None
	channel = None

	def __init__(self, server):
		self.server = server
		print("handler created for %s." % (server.name))
		return

	async def process_message(self, message):
		# Ignore message if it was sent by the bot.
		if message.author == client.user:
			return

		# Ensure that sillybot is being used by an admin.
		if message.content.startswith("$"):
			if not message.channel.permissions_for(message.author).administrator:
				await message.channel.send("sorry, you need to be an admin to use sillybot", delete_after = 5)
				return

		# Command to set category.
		if message.content.startswith("$category"):
			argument = message.content.split(" ", 1)
			if(len(argument) < 2):
				await message.channel.send("no category specified!", delete_after = 5)
				return
			argument = argument[1]

			self.category = discord.utils.get(message.channel.guild.categories, name = argument)
			if self.category is None:
				await message.channel.send("the category \"%s\" does not exist!" % argument, delete_after = 5)
				return

			await message.channel.send("the category is now set to \"%s\"" % argument, delete_after = 5)

		# Command to set channel.
		if message.content.startswith("$channel"):
			argument = message.content.split(" ", 1)
			if(len(argument) < 2):
				await message.channel.send("no channel specified!", delete_after = 5)
				return
			argument = argument[1]

			self.channel = discord.utils.get(message.channel.guild.channels, name = argument)
			if self.channel is None:
				await message.channel.send("the channel \"%s\" does not exist!" % argument, delete_after = 5)
				return

			await message.channel.send("the channel is now set to \"%s\"" % argument, delete_after = 5)

		# Command to print help.
		if message.content.startswith("$help"):
			info = str()
			info += "here are my available commands:"
			info += "$category - change the channel category from which to scrape posts"
			info += "$channel - change the channel into which to repost messages and files"
			info += "$dump - dump everything i know into chat"
			info += "$help - print this message to chat"
			await message.channel.send(info)
			return

		# Command to dump state to chat.
		if message.content.startswith("$dump"):
			info = str()
			info += "server name: %s\n" % ("None" if self.server is None else self.server.name)
			info += "category: %s\n" % ("None" if self.category is None else self.category.name)
			info += "channel: %s" % ("None" if self.channel is None else self.channel.name)
			await message.channel.send(info)

		# Repost into the given channel if a message was sent anywhere in a category. 
		if self.category is not None and self.channel is not None and message.channel.category == self.category:
			images = []
			for attachment in message.attachments:
				images.append(await attachment.to_file())

			repost = await self.channel.send(content = "in %s:\n%s" % (message.jump_url, message.content), files = images)
			await repost.edit(suppress = True)

intents = discord.Intents.default()
intents.message_content = True

client = rpbot(intents = intents)
client.run(os.environ["TOKEN"])
