# I'm putting this super class here to enforce structure on Abhay and 
#     in case we need to add other functionality to stuff

class Feature :
	def extract(self, game, player_color) :
		raise NotImplementedError()
	# straight