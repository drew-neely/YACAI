from timer import Timer
from big_array import BigArray
import chess
import unmove_generator # add unmove functions to chess.Board

class Tablebase :

	def __init__(self, name) :
		self.name = name
		self.table = BigArray(name, self.len, self.bytes_per_entry)

	def build(self) :
		raise NotImplementedError("Tablebase.build()")

	def checkmate_positions(self) :
		raise NotImplementedError("Tablebase.checkmate_positions()")

	def index(self, board) :
		raise NotImplementedError("Tablebase.index(board)")

	def set_dtm(self, index, winner, depth_to_mate) :
		raise NotImplementedError("Tablebase.set_dtm(board)")

	def get_dtm(self, index) :
		raise NotImplementedError("Tablebase.get_dtm(board)")

	@property
	def len(self) :
		raise NotImplementedError("Tablebase.len")

	@property
	def bytes_per_entry(self) :
		raise NotImplementedError("Tablebase.bytes_per_entry")

	@property
	def writable(self) :
		return self.table.writable

	def __getitem__(self, index):
		if isinstance(index, chess.Board) :
			return self.table[self.index(index)]
		elif isinstance(index, int) :
			return self.table[index]
		else :
			raise ValueError()

	def __setitem__(self, index, value):
		if isinstance(index, chess.Board) :
			self.table[self.index(index)] = value
		elif isinstance(index, int) :
			self.table[index] = value
		else :
			raise ValueError()

	def flush(self) :
		self.table.flush()