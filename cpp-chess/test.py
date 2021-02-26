from ctypes import *
import pathlib
from cpp_chess import Board, Move
from chess import Board as PyBoard
from time import time
from random import choice

if __name__ == "__main__":

	starting_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

	print("...")
	board = Board()
	py_board = PyBoard()
	count = 0
	for i in range(0, 1000) :
		move = None
		moves = []
		while(True) :
			if move != None :
				board.make_move(move)
				py_board.push(move)
			fen = board.get_fen()
			passed = fen == py_board.fen()
			if(not passed) :
				print(fen)
				print(PyBoard(fen))
				print("CORRECT" if passed else "INCORRECT - should be:\n"+py_board.fen())
				print("moves -\n", [m.uci() for m in moves])
				print("\n-------------")
				break
			if py_board.is_game_over(claim_draw = True) :
				if((i + 1) % 1 == 0) :
					print(f"GAME {i+1} OVER... {len(moves)} moves")
				break
			else :
				count += 1
				move = choice([m for m in py_board.legal_moves])
				# print(move)
				moves.append(move)
		board.free()
		board = Board()
		py_board = PyBoard()

	print(f"{count} moves played")

	# count = 100000

	# start = time()
	# for i in range(count) :
	# 	board = Board()
	# 	board.free()
	# end = time()
	# print(f"total: {end - start}\n per create/free: {(end - start) / count}")


