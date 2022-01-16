from timer import Timer
from big_array import BigArray
from tablebase import Tablebase
from indexing import get_kings_index_np
import chess
import unmove_generator # add unmove functions to chess.Board


class KQk(Tablebase) :

	def __init__(self) :
		super().__init__("KQk")

	def get_dtm(self, index) :
		value = self[index]
		winner = (value & 0b11000000) >> 6
		if winner == 1 :
			winner = chess.WHITE
		elif winner == 2 :
			winner = chess.BLACK
		else :
			winner = None
		dtm = value & 0b00111111
		return (winner, dtm)


	def set_dtm(self, index, winner, depth_to_mate) :
		if winner == chess.WHITE :
			winner = 1
		elif winner == chess.BLACK :
			winner = 2
		else :
			winner = 0
		if depth_to_mate > 2 ** 6 :
			raise ValueError("dtm must fit in 6 bits for KQk endgame")
		value = (winner << 6) | depth_to_mate
		self[index] = value



	def build(self) :
		if not self.writable :
			raise Exception("Cannot build non-writable Tablebase")
		mates = self.checkmate_positions()
		print(f"found {len(mates)} checkmate positions")
		for idx in mates :
			self.set_dtm(idx, chess.WHITE, 0)

		btmL_pos = mates
		wtmW_pos = {}
		depth = 1
		print("Starting tb generation")
		while btmL_pos :
			print()
			print(f"depth: {depth}, len(btmL_pos): {len(btmL_pos)}")
			# start by looking at btmL positions
			for _, board in btmL_pos.items() :
				# all parents of btmL positions are wtmW positions with dtm 1 larger
				for unmove in board.unmoves :
					new_board = board.copy()
					new_board.unpush(unmove)
					widx = self.index(new_board)
					cur_winner = self.get_dtm(widx)[0]					
					assert cur_winner != chess.BLACK
					if cur_winner is None : # no mates found yet
						wtmW_pos[widx] = new_board
						self.set_dtm(widx, chess.WHITE, depth)
			btmL_pos.clear()
			depth += 1
			print(f"depth: {depth}, len(wtmW_pos): {len(wtmW_pos)}")
			for _, board in wtmW_pos.items() :
				for unmove in board.unmoves :
					new_board = board.copy()
					new_board.unpush(unmove)
					is_loss = True
					do_print = (lambda x: None) if self.index(new_board) == 32625 else (lambda x: None)
					do_print(new_board)
					for move in new_board.legal_moves :
						do_print("")
						do_print(move)
						if new_board.is_capture(move) : # transition to diff tablebase
							is_loss = False
							do_print("Capture")
							break
						new_board.push(move)
						do_print(new_board)
						adj_idx = self.index(new_board)
						res = self.get_dtm(adj_idx)[0]
						do_print(f"idx = {adj_idx}")
						do_print(f"winner = {res}")
						if res != chess.WHITE :
							is_loss = False
							do_print("Not Win")
							new_board.pop()
							break
						new_board.pop()
					if is_loss :
						bidx = self.index(new_board)
						btmL_pos[bidx] = new_board
						self.set_dtm(bidx, chess.WHITE, depth)
					do_print("~~~~~~~~~~~~~~~~~~~~~~~~~")
			wtmW_pos.clear()
			depth += 1
		print()
		print(f"depth: {depth}, len(btmL_pos): {len(btmL_pos)}")

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
