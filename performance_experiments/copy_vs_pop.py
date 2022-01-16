# EXPERIMENT: testing if its faster to copy a board to test moves or push and pop from it
# RESULT: pushing and poping moves instead of copying the board yields a speedup for that
#	step alone of between 1.32 and 1.43 (95% confidence interval n=15)
# CONCLUSION: 
# 	The board must either be copied and pushed to or pushed to and popped from once per move tested.
#	Assume an average of 20 available moves for any given position (this number is not based on 
# 	anything other than a guess) and an average game length of 60 full moves (also not based on anything).
#	In two generations with p=32, n=3, 186 matches are played. Thus, 223,200 moves are tested. This gives 
#	the potential to reduce the runtime at testing configuration by about 20 seconds based on the amount of
#	time both versions take.
#	Additionally, this step apparently occupies somewhere around 40% of the time spent in simulation, which is huge.

import chess
import timeit

def copy_board() :
	board = chess.Board()
	for move in board.legal_moves :
		next_state = board.copy(stack=False)
		next_state.push(move)
		next_state.king(chess.WHITE)

def push_pop() :
	board = chess.Board()
	for move in board.legal_moves :
		board.push(move)
		board.king(chess.WHITE)
		board.pop()

def init_board() :
	board = chess.Board()

def legal_moves_gen() :
	board = chess.Board()
	for move in board.legal_moves :
		pass

def kings() :
	board = chess.Board()
	for move in board.legal_moves :
		board.king(chess.WHITE)

if __name__ == "__main__" :
	n = int(223200 / 10)
	tests = ["copy_board", "push_pop", "init_board", "legal_moves_gen", "kings"]
	result = {}
	for test in tests :
		result[test] = timeit.timeit(test+"()", setup="from __main__ import "+test, number=n)
		print(test+"\t\t", result[test])
	print("copy_board time = \t", result["copy_board"]- result["kings"])
	print("push_pop time = \t", result["push_pop"]- result["kings"])
	print("speedup = \t\t", (result["copy_board"]- result["kings"])/(result["push_pop"]- result["kings"]))
