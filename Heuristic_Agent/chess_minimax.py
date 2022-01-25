
import chess
from minimax import Minimax
from eval import get_eval
from score import Score
from transposition_table import TranspositionTable

class ChessMinimax(Minimax) :
	def __init__(self, board, depth, color=chess.WHITE, pruning=True, t_table=True, verbose=False):
		self.board = board
		if t_table :
			self.t_table = TranspositionTable()
			self.t_table_hits = 0
		else :
			self.t_table = None
		Minimax.__init__(self, depth, maxing= color==chess.WHITE, pruning=pruning, verbose=verbose)
		
	def children(self) :
		return list(self.board.legal_moves)

	def eval(self) :
		if self.t_table != None :
			fen = self.board.fen()
			if fen in self.t_table :
				self.t_table_hits += 1
				return self.t_table[fen]
			else :
				score = get_eval(self.board)
				self.t_table[fen] = score
				return score
		else :
			return get_eval(self.board)
		

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
		if self.t_table != None :
			print(f"num_t_table_hits = {self.t_table_hits} ({round(self.t_table_hits/self.num_evaled*10000)/100}%)")
		print(f"depth = {self.search_depth}, maxing = {self.search_maxing}, best choice = {self.best_choice}")
		print(f"depth 0 eval = {self.eval()}")
		print(f"depth {self.search_depth} eval = {self.best_quality}")
		print()