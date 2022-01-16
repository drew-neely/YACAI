import os, sys
import neat
import pickle
import chess
import time
from math import inf
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agent import Agent, extractors

def print_dict(dict, depth = 0) :
	preface = ''.join(['\t']*depth)
	if len(dict) == 0 :
		print(preface + "[]")
	elif dict[list(dict.keys())[0]] == None:
		print(preface + "[" + ','.join([m.uci() for m in dict.keys()]) + "]")
	else :
		for (move, d) in dict.items() :
			print(preface + move.uci() + ":")
			print_dict(d, depth=depth+1)

def get_agent_from_pickle(pickle_name) :
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, '../Config')
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)
    file = open(pickle_name, "rb")
    genome = pickle.load(file)
    net = neat.nn.FeedForwardNetwork.create(genome, config)
    return Agent(net)

agent = get_agent_from_pickle("best_iter110.pickle")

num_evaled = 0
def get_quality(board, moves) :
	global agent, num_evaled
	if not moves and board.is_checkmate(): # game is over
		return inf
	num_evaled += 1
	features = []
	for f in extractors :
		res = f.extract(board, board.turn)
		features += res
	return agent.net.activate(tuple(features))[0]

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

# returns (<best achievable quality>, [<moves to get to best state>])
def minimax(board, moves, depth, alpha=-inf, beta=inf, maxing=True) :
	if depth == 0 or not moves :
		return (get_quality(board, moves), [])
	
	best_quality = -inf if maxing else inf
	best_mvs = None
	best_move = None
	for (move, next_moves) in moves.items() :
		# print(''.join(["\t"]*(3-depth)) + move.uci(), best_quality)
		board.push(move)
		(quality, mvs) = minimax(board, next_moves, depth - 1, alpha, beta, not maxing)
		if (maxing and quality >= best_quality) or (not maxing and quality <= best_quality) :
			best_quality = quality
			best_mvs = mvs
			best_move = move
		if maxing and quality > alpha :
			alpha = quality
		elif not maxing and quality < beta :
			beta = quality
		board.pop()
		if beta <= alpha :
			break
	# print(''.join(["\t"]*(3-depth)) + "BEST:", best_quality, best_mvs)
	return (best_quality, [best_move] + best_mvs)






##################################################################
##################################################################
##################################################################
start_time = time.time()

board = chess.Board()
(moves, depth, leaves) = get_move_tree(board, min_depth=5) #, max_nodes=1000)

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

(quality, moves) = minimax(board, moves, depth)

end_time = time.time()
##  ##  ##  ##  ##  ##  ##  ##  

print("quality: ", quality)
print("moves: ", moves)
print("looked at: ",num_evaled,"/",leaves)
print("time: ", end_time - start_time)

##################################################################