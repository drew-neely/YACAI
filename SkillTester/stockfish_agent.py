import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from stockfish import Stockfish
import chess
from agent import Agent

# Will work when run on either of Drew's or sunbeam's computer
#     if run on different computer, probs will need diff binary
stockfish_location = "stockfish" if sys.platform == "darwin" else "stockfish_20090216_x64.exe"

class Stockfish_Agent(Agent) :

	def __init__(self, skill_level, depth=10) :
		super().__init__()
		self.stockfish = Stockfish(stockfish_location, parameters={"Threads":4})
		self.stockfish.set_depth(depth)
		self.stockfish.set_skill_level(skill_level)

	def get_move(self, board, color) :
		assert board.turn == color, "Stockfish asked to make a move when it's not its turn"
		self.stockfish.set_fen_position(board.fen())
		move = self.stockfish.get_best_move_time(100)
		return chess.Move.from_uci(move)
		