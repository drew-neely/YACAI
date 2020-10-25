import neat
import pickle
from agent import Agent

filename = "best_iter11_p=8_n=4.pickle"

class AI_Player :
	def __init__(self) :
		global filename
		best = pickle.load(open(filename, "rb"))
		net = neat.nn.FeedForwardNetwork.create(best, config)
		self.agent = Agent(net)
	
	def get_move(self, board, color) :
		return self.agent.get_move(board, color)