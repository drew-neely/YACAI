import os, sys
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "GameGUI"))
import chess

from heuristic_agent import Heuristic_Agent
from game import start_game

if __name__ == "__main__" :
	start_game("user", Heuristic_Agent(5), board=chess.Board("4k3/pppppppp/8/8/8/8/PPPPPPPP/3K4 w - - 0 1"))
	# start_game(Heuristic_Agent(4), "user", board=chess.Board("4k3/pppppppp/8/8/8/8/PPPPPPPP/3K4 w - - 0 1"), perspective=chess.BLACK)