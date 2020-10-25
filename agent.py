import chess
import math


from featureExtraction import * 

# List of instaces of objects which are subclasses of Feature
extractors = [PointDifference()]

class Agent :

	def __init__(self, net) :
		self.net = net

	# return a move as a string when given a board and neural net to evaluate a board
	def get_move(self, board, color) :
		assert board.turn == color, "Agent asked to make a move when it's not his turn"
		assert not board.is_game_over()

		moves = board.legal_moves
		max_quality = -math.inf
		best_move = None

		for move in moves :
			next_state = board.copy(False)
			next_state.push_san(move)
			features = tuple([f.extract(next_state, color) for f in extractors])
			quality = self.net.activate(features)
			if(quality > max_quality) :
				max_quality = quality
				best_move = move
		
		assert best_move != None
		return best_move

