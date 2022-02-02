import sys, os
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "SkillTester"))
from skillTester import run_matches
from heuristic_agent import Heuristic_Agent
from transposition_table import TranspositionTable
import chess

if __name__ == "__main__" :
	t_table = TranspositionTable()
	agent = Heuristic_Agent(0, timeout=10, pruning=True, t_table=t_table, node_ordering=True, it_deepening=True, verbose=False)
	run_matches(agent, 1, 20, board = chess.Board("4k3/pppppppp/8/8/8/8/PPPPPPPP/3K4 w - - 0 1"))

