from timer import Timer
from big_array import BigArray
from tablebase import Tablebase
from indexing import get_value_matrix
import chess
import unmove_generator # add unmove functions to chess.Board


class KQk(Tablebase) :

	def __init__(self) :
		super().__init__("KQk")

	def index(self, board) :
		index = 0
		found = 0
		matrix = get_value_matrix(board, includes_pawns=False)
		for sq in chess.SQUARES :
			piece = board.piece_at(sq)
			if piece :
				found += 1
				if piece.piece_type == chess.KING and piece.color == chess.WHITE :
					index += matrix[sq] * (64 ** 2) * 2
				elif piece.piece_type == chess.KING and piece.color == chess.BLACK :
					index += matrix[sq] * 64 * 2
				elif piece.piece_type == chess.QUEEN and piece.color == chess.WHITE :
					index += matrix[sq] * 2
				else :
					assert False
				if found >= 3 :
					break
		index += 1 if board.turn == chess.WHITE else 0
		return index
		

	@property
	def len(self) :
		return 10 * 64 * 64 * 2

	@property
	def bytes_per_entry(self) :
		return 1
