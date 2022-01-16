import chess
from math import inf as INFINITY

from featureExtraction import * 

# List of instaces of objects which are subclasses of Feature
extractors = [
				PointDifference(), simpleFeatures(), TwoOfAKind(), CheckCheckmate(), 
				PawnDistance(), AvgDisFromKing(), UnitDisFromKing(), NumOfLegalMoves(),
				NumAttackDefendMoves()
			]

agentCount = 0

class Agent :

	def __init__(self, net) :
		global agentCount
		self.net = net
		self.id = agentCount
		agentCount += 1

	# return a move as a string when given a board and neural net to evaluate a board
	def get_move(self, board, color) :
		assert board.turn == color, "Agent asked to make a move when it's not his turn"

		moves = board.legal_moves
		max_quality = -INFINITY
		best_move = None

		for move in moves :
			board.push(move)
			features = []
			for f in extractors :
				res = f.extract(board, color)
				features += res
			quality = self.net.activate(tuple(features))[0]
			if quality > max_quality :
				max_quality = quality
				best_move = move
			board.pop()
		
		assert best_move != None
		return best_move


import os, neat, pickle

def get_agent_from_pickle(pickle_name) :
	local_dir = os.path.dirname(__file__)
	config_path = os.path.join(local_dir, 'Config')
	config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
						 neat.DefaultSpeciesSet, neat.DefaultStagnation,
						 config_path)
	file = open(pickle_name, "rb")
	genome = pickle.load(file)
	net = neat.nn.FeedForwardNetwork.create(genome, config)
	return Agent(net)