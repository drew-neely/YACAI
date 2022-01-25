



class TranspositionTable :
	
	def __init__(self) :
		self.table = {}
	
	def __getitem__(self, id) :
		# use get instead of [] to get None if id is not in table
		return self.table.get(id)

	def __setitem__(self, id, value) :
		self.table[id] = value

	def __contains__(self, id) :
		return id in self.table
