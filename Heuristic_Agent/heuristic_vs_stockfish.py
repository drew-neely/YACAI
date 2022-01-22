import sys, os
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "SkillTester"))
from skillTester import run_matches
from heuristic_agent import Heuristic_Agent
import chess

if __name__ == "__main__" :
	run_matches(Heuristic_Agent(5), 1, 20, board = chess.Board("4k3/pppppppp/8/8/8/8/PPPPPPPP/3K4 w - - 0 1"))

