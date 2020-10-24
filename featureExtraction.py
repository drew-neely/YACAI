import chess

from feature import Feature

class ExampleFeature(Feature) :
	def extract(self, game) :
		return 50