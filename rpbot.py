import discord
import json
import random
import os

MOVES = ["jab", "cross", "hook", "uppercut", # Punches.
"roundhouse", "front kick", "side kick", "back kick"] # Kicks

class rpbot(discord.Client):
	# Array of server handlers.
	handlers = dict()

	def __init__(self, intents):
		super().__init__(intents = intents)

	async def on_ready(self):
		print("%s is logged in!" % (client.user))

	# Initialize an entry in handlers for the given server if one isn't already made.
	async def check_handler(self, server):
		if not server in self.handlers:
			self.handlers[server] = server_handler(discord.utils.get(self.guilds, id = server))
			await self.handlers[server].load_state()


	async def on_message(self, message):
		await self.check_handler(message.guild.id)
		await self.handlers[message.guild.id].process_message(message)
		await self.handlers[message.guild.id].update_directory()


	async def on_message_delete(self, message):
		await self.check_handler(message.guild.id)
		await self.handlers[message.guild.id].process_deletion(message)

	async def on_message_edit(self, message):
		await self.check_handler(message.guild.id)
		await self.handlers[message.guild.id].process_edit(message)

class server_handler:
	server = None
	category = None
	channel = None
	directory = None

	def __init__(self, server):
		self.server = server
		print("handler created for %s." % (server.name))
		return

	async def process_message(self, message):
		# Ignore message if it was sent by the bot.
		if message.author == client.user:
			return

		# Combo generator.
		if message.content.startswith("$combo"):
			argument = message.content.split(" ", 1)
			if(len(argument) < 2):
				await message.channel.send("no argument specified!", delete_after = 5)
				return
			argument = int(argument[1])

			info = str()
			for index in range(0, argument):
				info += random.choice(MOVES)
				if(index < argument - 1):
					info += ", "

			await message.channel.send(info)

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
				await message.channel.send("no argument specified!", delete_after = 5)
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
				await message.channel.send("no argument specified!", delete_after = 5)
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
			info += "hello! i'm sillybot. i watch a given channel category and repost its messages into a given channel.\n" 
			info += "here are my available commands:\n"
			info += "$help - print this message to chat\n"
			info += "$category <category name>- change the channel category from which to scrape posts\n"
			info += "$channel <channel name> - change the channel into which to repost messages and files\n"
			info += "$directory - create a message wherein i hold a live directory of all channels and threads within the category\n"
			info += "$save - save my state, including category, channel, and directory\n"
			info += "$load - loads state, mostly for debugging\n"
			info += "$dump - dump everything i know into chat\n"
			info += "$combo <length> - print a sequence of attacks to chat."
			await message.channel.send(info)
			return

		# Command to dump state to chat.
		if message.content.startswith("$dump"):
			info = str()
			info += "server: %s\n" % ("None" if self.server is None else self.server.name)
			info += "category: %s\n" % ("None" if self.category is None else self.category.name)
			info += "channel: %s\n" % ("None" if self.channel is None else self.channel.jump_url)
			info += "directory: %s" % ("None" if self.directory is None else self.directory.jump_url)
			await message.channel.send(info)

		# Create directory listing.
		if message.content.startswith("$directory"):
			self.directory = await message.channel.send("<3")
			await self.update_directory()

		# Save state.
		if message.content.startswith("$save"):
			await self.write_state()
			await message.channel.send("saved state to file", delete_after = 5)

		# Load state.
		if message.content.startswith("$load"):
			if os.path.isfile(str(self.server.id) + ".json"):
				with open(str(self.server.id) + ".json", "r", encoding = "utf-8") as file_handle:
					await self.load_state(json.load(file_handle))
			await message.channel.send("loaded state from file")

		# Repost into the given channel if a message was sent anywhere in a category. 
		if self.category is not None and self.channel is not None and message.channel.category == self.category:
			images = []
			for attachment in message.attachments:
				images.append(await attachment.to_file(spoiler = attachment.is_spoiler()))

			repost = await self.channel.send(content = "%s %s" % (message.jump_url, message.content), files = images)
			await repost.edit(suppress = True)

		# Reconstruct channel.
		if message.content.startswith("$reconstruct"):
			if self.channel is None:
				await message.channel.send("no given channel!")
				return

			async for repost in self.channel.history(limit = None):
				try:
					await repost.delete()
				except:
					print("can't delete message: %s" % (repost.jump_url))

			messages = []

			for channel in self.category.channels:
				if hasattr(channel, "history"):
					async for old_message in channel.history(limit = None):
						messages.append(old_message)

				if hasattr(channel, "threads"):
					for thread in channel.threads:
						async for old_message in thread.history(limit = None):
							messages.append(old_message)

			messages.sort(key = lambda old_message: old_message.created_at)

			for old_message in messages:
				images = []
				for attachment in old_message.attachments:
					images.append(await attachment.to_file(spoiler = attachment.is_spoiler()))

				repost = await self.channel.send(content = "%s %s" % (old_message.jump_url, old_message.content), files = images)
				await repost.edit(suppress = True)

	async def process_deletion(self, message):
		if self.channel is None:
			return

		async for repost in self.channel.history(limit = 16):
			if repost.content.startswith(message.jump_url):
				await repost.delete()

	async def update_directory(self):
		if self.directory is None:
			return

		info = str()

		if self.category is None:
			return None

		# Iterate through text channels and their threads.
		for channel in self.category.channels:
			if not hasattr(channel, "threads") or len(channel.threads) < 1:
				info += channel.jump_url + "\n"

		info += "\n"
		for channel in self.category.channels:
			if hasattr(channel, "threads") and len(channel.threads) > 0:
				info += channel.jump_url + "\n"
				for thread in channel.threads:
					info += "└───" + thread.jump_url + "\n"
				info += "\n"

		await self.directory.edit(content = info)

	async def write_state(self):
		with open("data/" + str(self.server.id) + ".json", "w", encoding = "utf-8") as file_handle:
			json.dump({
				"category": None if self.category is None else self.category.id,
				"channel": None if self.channel is None else self.channel.id,
				"directory": {
					"channel_id": None if self.directory is None else self.directory.channel.id,
					"id":  None if self.directory is None else self.directory.id
				}
			}, file_handle);

	async def load_state(self):
		if os.path.isfile("data/" + str(self.server.id) + ".json"):
			with open("data/" + str(self.server.id) + ".json", "r", encoding = "utf-8") as file_handle:
				object = json.load(file_handle)
				if object is None:
					return

		self.category = discord.utils.get(self.server.categories, id = object["category"])
		self.channel = discord.utils.get(self.server.channels, id = object["channel"])
		self.directory = discord.utils.get(self.server.channels, id = object["directory"]["channel_id"])
		self.directory = None if self.directory is None else await self.directory.fetch_message(object["directory"]["id"])
		return

intents = discord.Intents.default()
intents.message_content = True

client = rpbot(intents = intents)
client.run(os.environ["TOKEN"])
