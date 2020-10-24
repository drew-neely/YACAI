"""
2-input XOR example -- this is most likely the simplest possible example.
"""

from __future__ import print_function
import os
import neat
import visualize

# 2-input XOR inputs and expected outputs.
# xor_inputs = [(0.0, 0.0), (0.0, 1.0), (1.0, 0.0), (1.0, 1.0)]
# xor_outputs = [   (0.0,),     (1.0,),     (1.0,),     (0.0,)]

inputs = [(1,), (2,), (3,), (4,), (5,), (6,)]
outputs = [(5,), (10,), (15,), (20,), (25,), (30,)]


# def eval_genomes(genomes, config):
#     for genome_id, genome in genomes:
#         genome.fitness = 4.0
#         net = neat.nn.FeedForwardNetwork.create(genome, config)
#         for xi, xo in zip(xor_inputs, xor_outputs):
#             output = net.activate(xi)
#             genome.fitness -= (output[0] - xo[0]) ** 2

def eval_genomes(genomes, config):
	for genome_id, genome in genomes:
		# genome.fitness = 4.0
		net = neat.nn.FeedForwardNetwork.create(genome, config)
		diff = 0
		for i, o in zip(inputs, outputs):
			output = net.activate(i)
			# diff = 2.718 ** (-1 * ((output[0] / i[0] - 5) ** 2))
			diff += output[0] - o[0]
			# diff += 
		genome.fitness = diff



def run(config_file):
	# Load configuration.
	config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
						 neat.DefaultSpeciesSet, neat.DefaultStagnation,
						 config_file)

	# Create the population, which is the top-level object for a NEAT run.
	p = neat.Population(config)

	# Add a stdout reporter to show progress in the terminal.

	# p.add_reporter(neat.StdOutReporter(True))
	stats = neat.StatisticsReporter()
	# p.add_reporter(stats)
	# p.add_reporter(neat.Checkpointer(5))

	# Run for up to 300 generations.
	winner = p.run(eval_genomes, 100)

	# Display the winning genome.
	print('\nBest genome:\n{!s}'.format(winner))

	# Show output of the most fit genome against training data.
	print('\nOutput:')
	winner_net = neat.nn.FeedForwardNetwork.create(winner, config)
	for xi, xo in zip(inputs, outputs):
		output = winner_net.activate(xi)
		print("input {!r}, expected output {!r}, got {!r}".format(xi, xo, output))

	# node_names = {-1:'A', -2: 'B', 0:'A XOR B'}
	# visualize.draw_net(config, winner, True, node_names=node_names)
	# visualize.plot_stats(stats, ylog=False, view=True)
	# visualize.plot_species(stats, view=True)

	# p = neat.Checkpointer.restore_checkpoint('neat-checkpoint-4')
	# p.run(eval_genomes, 100)


if __name__ == '__main__':
	# Determine path to configuration file. This path manipulation is
	# here so that the script will run successfully regardless of the
	# current working directory.
	local_dir = os.path.dirname(__file__)
	config_path = os.path.join(local_dir, 'Config')
	run(config_path)