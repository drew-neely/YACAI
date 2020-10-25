"""
2-input XOR example -- this is most likely the simplest possible example.
"""

from __future__ import print_function
import os
import neat
import visualize

from agent import Agent
from referee import Referee

def eval_genomes(genomes, config):
	ref = Referee()

	nets = [ neat.nn.FeedForwardNetwork.create(genome[1], config) for genome in genomes ]
	agents = [ Agent(net) for net in nets ]
	
	ranks = ref.get_ranks(agents, 1)

	for (genome, rank) in zip(genomes, ranks) :
		genome[1].fitness = rank



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
	winner = p.run(eval_genomes, 2)

	# Display the winning genome.
	print('\nBest genome:\n{!s}'.format(winner))

	# Show output of the most fit genome against training data.
	print('\nOutput:')
	winner_net = neat.nn.FeedForwardNetwork.create(winner, config)

	# node_names = {-1:'A', 0:'A * 5'}
	visualize.draw_net(config, winner, True) # , node_names=node_names)
	visualize.plot_stats(stats, ylog=False, view=True)
	visualize.plot_species(stats, view=True)

	# p = neat.Checkpointer.restore_checkpoint('neat-checkpoint-4')
	# p.run(eval_genomes, 100)


if __name__ == '__main__':
	# Determine path to configuration file. This path manipulation is
	# here so that the script will run successfully regardless of the
	# current working directory.
	local_dir = os.path.dirname(__file__)
	config_path = os.path.join(local_dir, 'Config')
	run(config_path)