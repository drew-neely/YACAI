import chess
import math


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
		max_quality = -math.inf
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


