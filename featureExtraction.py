import chess

from feature import Feature

class ExampleFeature(Feature) :
	
	# game is a chess board from the chess library
	# player_color is one of chess.WHITE or chess.BLACK
	def extract(self, game, player_color) :
		return 50

class PointDifference(Feature) :
	
	piece_values = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3, chess.ROOK: 5, chess.QUEEN: 9}

	# game is a chess board from the chess library
	# player_color is one of chess.WHITE or chess.BLACK
	def extract(self, game, player_color) :
		pieces = []
		for sq in chess.SQUARES :
			p = game.piece_at(sq)
			if p != None and p.piece_type != chess.KING:
				pieces.append(p)

		total = 0
		for p in pieces :
			value = self.piece_values[p]
			if player_color != p.color :
				value *= -1
			total += value
		
		return total

		



		