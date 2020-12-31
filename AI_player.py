import neat
import pickle
from agent import Agent

filename = "best_iter11_p=8_n=4.pickle"

class AI_Player :
	def __init__(self) :
		global filename
		best = pickle.load(open(filename, "rb"))
		local_dir = os.path.dirname(__file__)
		config_path = os.path.join(local_dir, 'Config')
		config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)
		net = neat.nn.FeedForwardNetwork.create(best, config)
		self.agent = Agent(net)
	
	def get_move(self, board, color) :
		return self.agent.get_move(board, color)


if __name__ == '__main__':
	board = chess.Board()
	white = AI_Player()
	black = AI_Player()
	colors = {chess.WHITE: white, chess.BLACK: black}
	while not board.is_game_over() :
		