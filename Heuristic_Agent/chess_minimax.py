
import chess
from minimax import Minimax
from eval import get_eval

class ChessMinimax(Minimax) :
	def __init__(self, board, depth, color=chess.WHITE, pruning=True):
		self.board = board
		super().__init__(depth, maxing= color==chess.WHITE, pruning=pruning)

	def children(self) :
		return list(self.board.legal_moves)

	def eval(self) :
		return get_eval(self.board)

	def apply(self, choice) :
		self.board.push(choice)

	def unapply(self) :
		self.board.pop()