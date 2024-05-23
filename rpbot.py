import discord
import json
import os
import asyncio
from server_handler import server_handler

class rpbot(discord.Client):
	handlers = dict()

	def __init__(self, intents):
		super().__init__(intents = intents)

	async def on_ready(self):
		print("%s is logged in!" % (client.user))

		promises = list()
		for guild in self.guilds:
			handler = server_handler(self, guild)
			self.handlers[guild.id] = handler
			promises.append(handler.load())

		await asyncio.gather(* promises)
		return

	async def on_guild_join(self, guild):
		handler = server_handler(self)
		handler.server = guild
		print("handler initialized for server %s!" % (guild.name))
		return

	async def on_message(self, message):
		await self.handlers[message.guild.id].read_message(message)

intents = discord.Intents.default()
intents.message_content = True

client = rpbot(intents = intents)
client.run(os.environ["TOKEN"])
