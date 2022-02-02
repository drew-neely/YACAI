import os, sys
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "GameGUI"))
import chess

from heuristic_agent import Heuristic_Agent
from transposition_table import TranspositionTable
from game import start_game

if __name__ == "__main__" :
	t_table = TranspositionTable()
	agent = Heuristic_Agent(5, timeout=10, pruning=True, t_table=t_table, node_ordering=True, it_deepening=True, verbose=False)
	start_game("user", agent, board=chess.Board("4k3/pppppppp/8/8/8/8/PPPPPPPP/3K4 w - - 0 1"))
	# start_game(Heuristic_Agent(4), "user", board=chess.Board("4k3/pppppppp/8/8/8/8/PPPPPPPP/3K4 w - - 0 1"), perspective=chess.BLACK)