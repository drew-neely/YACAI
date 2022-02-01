
import chess
from minimax import Minimax
from eval import get_eval
from score import Score
from transposition_table import TranspositionTable

class ChessMinimax(Minimax) :
	def __init__(self, board, depth, color=chess.WHITE, pruning=True, t_table=True, node_ordering=True, verbose=False):
		self.board = board
		if t_table == True:
			self.t_table = TranspositionTable()
		elif isinstance(t_table, TranspositionTable) :
			self.t_table = t_table
		else :
			self.t_table = None
		self.node_ordering = node_ordering

		# stats to track
		if t_table :
			self.t_table_hits = 0
			self.t_table_miss = 0
			self.records = 0
			self.lookup_hits = 0
			self.lookup_miss = 0
		
		if t_table and node_ordering :
			self.internal_node_hits = 0
			self.internal_node_miss = 0
		elif node_ordering :
			self.internal_node_evals = 0

		Minimax.__init__(self, depth, maxing= color==chess.WHITE, pruning=pruning, verbose=verbose)
		
	def children(self) :
		
		if self.node_ordering :
			move_score_pairs = []
			for move in self.board.legal_moves :
				self.board.push(move)
				###### get score
				if self.t_table != None :
					fen = self.board.fen()
					if (fen, 0) in self.t_table :
						self.internal_node_hits += 1
						score = self.t_table[(fen, 0)]
					else :
						self.internal_node_miss += 1
						score = get_eval(self.board)
						self.t_table[(fen, 0)] = score
				else :
					self.internal_node_evals += 1
					score = get_eval(self.board)
				###### 
				move_score_pairs.append((move, score))
				self.board.pop()
			move_score_pairs.sort(key = lambda x : x[1], reverse=True)
			return [ move for move, _ in move_score_pairs ]
		else :
			return list(self.board.legal_moves)

	def eval(self) :
		if self.t_table != None :
			fen = self.board.fen()
			if (fen, 0) in self.t_table :
				self.t_table_hits += 1
				return self.t_table[(fen, 0)]
			else :
				self.t_table_miss += 1
				score = get_eval(self.board)
				self.t_table[(fen, 0)] = score
				return score
		else :
			return get_eval(self.board)

	def record(self, quality, depth, maxing) :
		if self.t_table != None :
			fen = self.board.fen()
			self.t_table[(fen, depth)] = quality
			self.records += 1
		else :
			pass

	def lookup(self, depth, maxing) :
		if self.t_table != None :
			fen = self.board.fen()
			res = self.t_table[(fen, depth)]
			if res is not None :
				self.lookup_hits += 1
			else :
				self.lookup_miss += 1
			return res
		else :
			return None


	def apply(self, choice) :
		self.board.push(choice)

	def unapply(self) :
		self.board.pop()

	@property
	def min_eval(self) :
		return Score.checkmate(chess.BLACK)

	@property
	def max_eval(self) :
		return Score.checkmate(chess.WHITE)

	def inc_eval(self, e) :
		return e.inc()

	def __str__(self) :
		return str([str(m) for m in self.board.move_stack])

	def dump(self) :
		print("ChessMinimax search dump:")
		print(f"fen = {self.board.fen()}")
		print(f"num_evaled = {self.num_evaled}")

		if self.t_table is not None and not self.node_ordering :
			print(f"num_t_table_hits = {self.t_table_hits} ({round(self.t_table_hits/(self.t_table_hits+self.t_table_miss)*10000)/100 if self.t_table_hits+self.t_table_miss != 0 else 0}%)")

		if self.t_table != None :
			print(f"num_records = {self.records}")
			print(f"num_lookup_hits = {self.lookup_hits}/{self.lookup_hits+self.lookup_miss} ({round(self.lookup_hits/(self.lookup_hits+self.lookup_miss)*10000)/100}%)")
		if self.t_table != None and self.node_ordering :
			print(f"num_internal_node_hits = {self.internal_node_hits}/{self.internal_node_hits+self.internal_node_miss} ({round(self.internal_node_hits/(self.internal_node_hits+self.internal_node_miss)*10000)/100}%)")
		elif self.node_ordering :
			print(f"Internal node evals = {self.internal_node_evals}")
		print(f"depth = {self.search_depth}, maxing = {self.search_maxing}, best choice = {self.best_choice}")
		print(f"depth 0 eval = {self.eval()}")
		print(f"depth {self.search_depth} eval = {self.best_quality}")
		print(f"search time = {round(self.search_time*10)/10}s")
		print()