"""
2-input XOR example -- this is most likely the simplest possible example.
"""

from __future__ import print_function
import os
import neat
import visualize
import pickle

from agent import Agent
from referee import Referee

def eval_genomes(genomes, config):
	ref = Referee()

	nets = [ neat.nn.FeedForwardNetwork.create(genome[1], config) for genome in genomes ]
	agents = [ Agent(net) for net in nets ]
	
	ranks = ref.get_ranks(agents, 3)

	for (genome, rank) in zip(genomes, ranks) :
		genome[1].fitness = 2.718 ** (- rank / 1.5)



def run(config_file):
	# Load configuration.
	config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
						 neat.DefaultSpeciesSet, neat.DefaultStagnation,
						 config_file)

	# Create the population, which is the top-level object for a NEAT run.
	p = neat.Population(config)

	# Add a stdout reporter to show progress in the terminal.

	p.add_reporter(neat.StdOutReporter(True))
	stats = neat.StatisticsReporter()
	p.add_reporter(stats)
	p.add_reporter(neat.Checkpointer(5))

	# Run for up to 300 generations.
	for i in range(0, 20000) :
		winner = p.run(eval_genomes, 1)
		pickle.dump(winner, open("best_iter" + str(i) + ".pickle", "wb"))
		print(winner)


if __name__ == '__main__':
	# Determine path to configuration file. This path manipulation is
	# here so that the script will run successfully regardless of the
	# current working directory.
	local_dir = os.path.dirname(__file__)
	config_path = os.path.join(local_dir, 'Config')
	run(config_path)