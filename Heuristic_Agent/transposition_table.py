



class TranspositionTable :
	
	def __init__(self) :
		# self.table is indexed by <fen> and contains (<score>, <depth>)
		self.table = {}
	
	# id is <fen> or tuple of (<fen>, <required_depth>)
	#     if fen is in table, returns score only if required_depth <= existing_depth or
	#     id is just specified as fen
	def __getitem__(self, id) :
		if type(id) == tuple :
			if id[0] in self.table :
				score = self.table[id[0]]
				return score[0] if score[1] >= id[1] else None
			else : 
				return None
		elif type(id) == str :
			return self.table[id[0]] if id[0] in self.table else None
		else :
			raise ValueError("id must be tuple or str")

	# id is tuple of (<fen>, <depth>)
	# value is the score to be stored
	#     depth 0 implies the score is the result of a direct eval
	# value is always added to table (even if value has lower depth)
	# this should be acceptable since eval will only occur if depth is not large enough
	def __setitem__(self, id, value) :
		self.table[id[0]] = (value, id[1])

	# id is <fen> or tuple of (<fen>, <required_depth>)
	#     true if fen is in table and existing depth >= required_depth
	def __contains__(self, id) :
		if type(id) == tuple :
			return id[0] in self.table and self.table[id[0]][1] >= id[1]
		elif type(id) == str :
			return id[0] in self.table
		else :
			raise ValueError("id must be tuple or str")

