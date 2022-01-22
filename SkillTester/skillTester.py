import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import chess
import random
import time 
from multiprocessing import cpu_count, Pool


from yacai_agent import YACAI_Agent
from stockfish_agent import Stockfish_Agent
from match import Match, Result

def print_board(str) :
	emojis = "♔♕♗♘♙♚♛♝♞♟♖♜"
	text = "kqbnpKQBNPrR"
	for i in range(len(emojis)) :
		str = str.replace(text[i], emojis[i])
	print(str)

# runs 1 match (method is defined like this so it may be easily called by starmap)
# 	returns -1 => agent win, 0 => draw, 1 => stockfish win
def run_match(agent, stockfish_level, board = None) :
	if not board :
		board = chess.Board
	stockfish = Stockfish_Agent(stockfish_level)
	match = Match(agent, stockfish, random_colors = True)
	res = match.run(board = board)

	if res.winner_id == agent.id :
		print("Agent     won as", "white" if res.winner_id == res.white_id else "black")
	elif res.winner_id == stockfish.id :
		print("Stockfish won as", "white" if res.winner_id == res.white_id else "black")
	else :
		print("Game was Draw")

	if res.winner_id == agent.id :
		return -1
	elif res.winner_id == stockfish.id :
		return 1
	else :
		return 0

pool = Pool(cpu_count())

# runs number matches between agent1 and agent2
# 	returns (<# agent1 wins>, <# draws>, <# agent2 wins>)
def run_matches(agent, stockfish_level, number, board = None) :

	if not board :
		board = chess.Board()
		
	results = pool.starmap(run_match, [(agent, stockfish_level, board.copy()) for _ in range(number)])
	print(results)
	
if __name__ == "__main__" :
	agent = YACAI_Agent.from_file("best_iter110.pickle")
	
	run_matches(agent, 1, 12)
	