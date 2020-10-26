import neat
import pickle
import os
from chessAI.agent import Agent

filename = "./chessAI/best_iter110.pickle"

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