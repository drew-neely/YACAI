
import chess
from minimax import Minimax
from eval import get_eval

class ChessMinimax(Minimax) :
	def __init__(self, board, depth, color=chess.WHITE, pruning=True):
		super().__init__(board, depth, maxing= color==chess.WHITE, pruning=pruning)

	def children(self) :
		return list(self.node.legal_moves)

	def eval(self) :
		return get_eval(self.node)

	def apply(self, choice) :
		self.node.push(choice)

	def unapply(self) :
		self.node.pop()