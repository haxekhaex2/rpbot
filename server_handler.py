import os
import json
import types
from category_dump import category_dump

class server_handler:
	client = None
	server = None
	dumps = dict()

	def __init__(self, client, server):
		self.client = client
		self.server = server

	# Load state.
	async def load(self):
		path = "data/%s.json" % (self.server.id)

		# Load object from json, or set to None.
		try:
			file_handle = open(path, "r")
			obj = json.load(file_handle)
			print("loaded json for server %s" % (self.server.name))
			file_handle.close()
		except (IOError, ValueError):
			obj = None
			print("couldn't load json for server %s" % (self.server.name))
			return

		# Load attributes from object.
		for key, value in obj.items():
			print("key: %s, value: %s" % (key, value))

		return

	# Save state.
	async def save(self):
		# Write attributes to object.
		obj = dict()

		# Write file to disk.
		path = "data/%s.json" % (self.server.id)
		try:
			file_handle = open(path, "w")
			json.dump(obj, file_handle)
			print("saved json for server %s" % (self.server.name))
			file_handle.close()
		except IOError:	
			print("couldn't save json for server %s" % (self.server.name))
			return

		return

	# Read a message.
	async def read_message(self, message):
		arguments = message.content.split()
		if len(arguments) == 0:
			return

		match arguments[0]:
			case "$dump":
				async def dump():
					info = str()
					info += "client: %s\n" % (self.client.user.name)
					info += "server: %s\n" % (self.server.name)
					info += "dumps:\n"
					for key, value in self.dumps.items():
						print(type(attribute))
						channel_name = attribute.channel.name if attribute.channel is not None else None
						category_name = attribute.category.name if attribute.category is not None else None
						info += "\tname: %s, channel: %s, category: %s" % (key, channel_name, category_name)
					info += "\n"
					await message.channel.send(content = info)
				await dump()

			case "$create_dump":
				if len(arguments) > 1:
					self.dumps[arguments[1]] = category_dump()
					print(type(category_dump()))
					

			case "$destroy_dump":
				if len(arguments) > 1:
					del self.dumps[arguments[1]]
