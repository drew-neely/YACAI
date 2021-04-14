import sys
import neat, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agent import Agent, extractors
from match import Match, Result
import pickle

def make_agent(name, config) :
	genome = neat.genome.DefaultGenome(name)
	net = neat.nn.FeedForwardNetwork.create(genome, config)
	return Agent(net)

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

def run_match(config) :
	white = get_agent_from_pickle("best_iter110.pickle")
	black = get_agent_from_pickle("best_iter110.pickle")
	# white = make_agent("white", config)
	# black = make_agent("black", config)
	print("white id =", white.id)
	print("black id =", black.id)
	match = Match(white, black)
	result = match.run()
	print("winner id =", result.winner_id)
	print(result.moves)

if __name__ == "__main__" :
	local_dir = os.path.dirname(__file__)
	config_path = os.path.join(local_dir, '../Config')
	config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
						 neat.DefaultSpeciesSet, neat.DefaultStagnation,
						 config_path)
	run_match(config)