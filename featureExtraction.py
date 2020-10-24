import chess

from feature import Feature

class ExampleFeature(Feature) :
	
	# game is a chess board from the chess library
	# player_color is one of chess.WHITE or chess.BLACK
	def extract(self, game, player_color) :
		return 50