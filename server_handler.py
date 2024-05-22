class server_handler:
	client = None
	server = None

	def __init__(self, client):
		self.client = client

	# Load from the file at path, and initialize defaults.
	async def load(self, path):
		print("finished loading!")

	# Save to path.
	async def save(self, path):
		print("finished saving!")
