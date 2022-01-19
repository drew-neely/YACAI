
import chess
from minimax import Minimax
from eval import get_eval
from score import Score

class ChessMinimax(Minimax) :
	def __init__(self, board, depth, color=chess.WHITE, pruning=True, verbose=False):
		self.board = board
		super().__init__(depth, maxing= color==chess.WHITE, pruning=pruning, verbose=verbose)

	def children(self) :
		return list(self.board.legal_moves)

	def eval(self) :
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
		print(f"depth = {self.search_depth}, maxing = {self.search_maxing}, best choice = {self.best_path[0]}")
		print(f"best path = {self.best_path}")
		print(f"depth 0 eval = {self.eval()}")
		print(f"depth {self.search_depth} eval = {self.best_quality}")
		print()