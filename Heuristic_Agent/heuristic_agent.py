import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import chess
import time
import random
from math import inf
from random import shuffle

from agent import Agent
from minimax import Minimax

class Heuristic_Agent(Agent) :

	def __init__(self, depth) :
		self.depth = depth
		super().__init__()
		
	def get_move(self, board, color) :
		minimax = Minimax(board, self.depth, color=color, pruning=True)
		# minimax_np = Minimax(board, self.depth, color=color, pruning=False)
		# print("---")
		# print("pruning")
		minimax.dump()
		# print("no pruning")
		# minimax_np.dump()
		# if(minimax.best_quality != minimax_np.best_quality) :
		# 	print("MINIMAX mismatch")
		return minimax.best_moves[0]





def get_move_tree(board, min_depth=2, max_depth=10, max_nodes=0):
	moves = {move:None for move in board.legal_moves}
	depth = 1
	num_leaves = len(moves)
	while depth < min_depth or num_leaves < max_nodes and depth < max_depth :
		num_leaves = 0
		dicts = [moves] + [None] * (depth - 1) # len(dic)
		to_visit = [list(moves.keys())] + [[]] * (depth - 1)
		d = 0 # level to which to_visit is filled out
		while d != 0 or to_visit[0]:
			# print(board)
			# print()
			if not to_visit[d] :
				d -= 1
				board.pop()
			else :
				move = to_visit[d].pop()
				board.push(move) 
				if d + 1 == depth :
					dicts[d][move] = {m:None for m in board.legal_moves}
					num_leaves += len(dicts[d][move])
					board.pop()
				else :
					to_visit[d+1] = list(dicts[d][move].keys())
					dicts[d+1] = dicts[d][move]
					d += 1
		depth += 1
	return (moves, depth, num_leaves)


if __name__ == "__main__" :

	goto_depth = 6

	##################################################################
	##################################################################
	##################################################################
	start_time = time.time()

	board = chess.Board("4k3/pppppppp/8/8/8/8/PPPPPPPP/3K4 w - - 0 1")
	print(board)
	(moves, depth, leaves) = get_move_tree(board, min_depth=goto_depth) #, max_nodes=1000)

	end_time = time.time()
	##  ##  ##  ##  ##  ##  ##  ##  

	# print_dict(moves)
	print("leaves: ", leaves)
	print("depth: ", depth)
	print("time: ", end_time - start_time)
	##################################################################
	print("\n")
	##################################################################
	start_time = time.time()

	minimax = Minimax(board, goto_depth)

	end_time = time.time()
	##  ##  ##  ##  ##  ##  ##  ##  

	print("quality: ", minimax.best_quality)
	print("moves: ", minimax.best_moves)
	print(f"looked at (total): {minimax.num_evaled}/{leaves} ({round(minimax.num_evaled/leaves*10000)/100})% leaves")
	print("time: ", end_time - start_time)

	##################################################################