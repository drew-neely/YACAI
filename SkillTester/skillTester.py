import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from stockfish import Stockfish
import chess
import random
import time 

from agent import Agent, get_agent_from_pickle

def print_board(str) :
	emojis = "♔♕♗♘♙♚♛♝♞♟♖♜"
	text = "kqbnpKQBNPrR"
	for i in range(len(emojis)) :
		str = str.replace(text[i], emojis[i])
	print(str)

# Will work when run on either of Drew's or sunbeam's computer
#     if run on different computer, probs will need diff binary
stockfish_location = "stockfish" if sys.platform == "darwin" else "stockfish_20090216_x64.exe"

# agent is agent object to play
# stockfish skill level with elos approx : < !!! insert the elos here for reference>
# agent_is_white -> True = agent is white, False = stockfish is white, None = pick at random
# RETURN VALUE : True = agent won, False = stockfish won, None = draw
def runMatch(agent, stockfish_skill_level, agent_is_white=None):
	# init stockfish
	stockfish = Stockfish(stockfish_location, parameters={"Threads":4})
	stockfish.set_depth(5)
	stockfish.set_skill_level(stockfish_skill_level)

	# init chess board
	board = chess.Board()

	# Run match
		# < True = stockfishes turn, False = agents turn >
	agent_is_white = agent_is_white if agent_is_white != None else random.choice([True, False])
	turn = not agent_is_white
	while not board.is_game_over(claim_draw=True) :
		if turn :
			stock_move = stockfish.get_best_move_time(100)
			board.push_san(stock_move)
			stockfish.set_fen_position(board.fen())
		else:
			agent_move = agent.get_move(board, chess.WHITE if agent_is_white else chess.BLACK)
			board.push(agent_move)
			stockfish.set_fen_position(board.fen())
		# print_board(stockfish.get_board_visual())
		# input("Press Enter to continue...")
		turn = not turn

	# Get results
	result = board.result(claim_draw=True)
	if result == "1-0" :
		return agent_is_white
	elif result == "0-1" :
		return not agent_is_white
	elif result == "1/2-1/2" :
		return None
	else :
		assert False
			
		
	
if __name__ == "__main__" :
	agent = get_agent_from_pickle("best_iter110.pickle")
	for _ in range(100) :
		we_won = runMatch(agent, 15, True)
		print(we_won)
	