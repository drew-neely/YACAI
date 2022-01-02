from pickle import TRUE
import chess
from math import inf

from eval import get_eval

# Each minimax search is done as a class so that stats can be collected
class Minimax :

	def __init__(self, board, depth, alpha=-inf, beta=inf, color=chess.WHITE, pruning=True):
		self.board = board
		self.search_depth = depth
		self.search_alpha = alpha
		self.search_beta = beta
		self.search_maxing = color == chess.WHITE
		self.pruning = pruning
		
		# perf stats
		self.num_evaled = 0

		# perform the search
		(self.best_quality, self.best_moves) = self.search(depth, alpha, beta, color == chess.WHITE)

	# returns (<best achievable quality>, [<moves to get to best state>])
	def search(self, depth, alpha, beta, maxing) :
		moves = list(self.board.legal_moves)
		if depth == 0 or not moves :
			self.num_evaled += 1
			return (get_eval(self.board, self.search_depth-depth), [])

		best_quality = -inf if maxing else inf
		best_mvs = None
		best_move = None
		for move in moves:
			# print(''.join(["\t"]*(3-depth)) + move.uci(), best_quality)
			self.board.push(move)
			(quality, mvs) = self.search(depth - 1, alpha, beta, not maxing)
			if (maxing and quality >= best_quality) or (not maxing and quality <= best_quality) :
				best_quality = quality
				best_mvs = mvs
				best_move = move
			self.board.pop()
			if self.pruning :
				if maxing and quality > alpha :
					alpha = quality
				elif not maxing and quality < beta :
					beta = quality
				if (maxing and quality >= beta) or (not maxing and quality <= alpha) :
					break
				# if beta <= alpha :
				# 	break
		# print(''.join(["\t"]*(3-depth)) + "BEST:", best_quality, best_mvs)
		return (best_quality, [best_move] + best_mvs)

	def dump(self) :
		print("Minimax search dump:")
		print(f"num_evaled = {self.num_evaled}")
		print(f"depth = {self.search_depth}, maxing = {self.search_maxing}, best move = {self.best_moves[0]}")
		print(f"best moves = {self.best_moves}")
		print(f"position eval = {get_eval(self.board, 0)}")
		print(f"best eval = {self.best_quality}")
		print()