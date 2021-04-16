from timer import Timer
from big_array import BigArray
from tablebase import Tablebase
from indexing import get_kings_index_np
import chess
import unmove_generator # add unmove functions to chess.Board


class KQk(Tablebase) :

	def __init__(self) :
		super().__init__("KQk")

	# Take advantage of the fact that all KQk checkmates have the black king
	# 	on the edge of the board
	def checkmate_positions(self) :
		mates = {}
		bk_pos = [i for i in range(64) if i < 8 or i >= 56 or i%8 == 0 or i%8 == 7]
		for bk in bk_pos :
			br, bf = int(bk / 8), bk % 8
			for wk in range(64) :
				wr, wf = int(wk / 8), wk % 8
				if abs(br - wr) <= 1 and abs(bf - wf) <= 1 :
					continue
				if abs(br - wr) > 2 or abs(bf - wf) > 2 :
					continue
				for q in range(64) :
					if q == wk or q == bk :
						continue
					board = chess.Board(None)
					board.set_piece_at(wk, chess.Piece(chess.KING, chess.WHITE))
					board.set_piece_at(bk, chess.Piece(chess.KING, chess.BLACK))
					board.set_piece_at(q, chess.Piece(chess.QUEEN, chess.WHITE))
					board.turn = chess.BLACK
					if board.is_checkmate() :
						idx = self.index(board)
						if idx not in mates :
							mates[idx] = board
		return mates

		
			

	def index(self, board) :
		queen_index = None
		king_index, square_index_mat = get_kings_index_np(board)
		pieces = [(sq, board.piece_at(sq)) for sq in chess.SQUARES]
		pieces = [(sq, piece) for (sq, piece) in pieces if piece is not None and piece.piece_type != chess.KING]
		assert len(pieces) == 1
		assert pieces[0][1].piece_type == chess.QUEEN
		queen_index = square_index_mat[pieces[0][0]]
		q_sub = 0
		for color in [chess.WHITE, chess.BLACK] :
			if square_index_mat[board.king(color)] < queen_index :
				q_sub += 1
		queen_index -= q_sub
		assert queen_index < 62
		turn_index = 0 if board.turn == chess.WHITE else 1
		index = turn_index * 462 * 62 + king_index * 62 + queen_index
		return index
		

	@property
	def len(self) :
		return 2 * 462 * 62

	@property
	def bytes_per_entry(self) :
		return 1
