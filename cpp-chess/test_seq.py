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

	moves = ['a2a4', 'f7f6', 'h2h4', 'b8a6', 'e2e4', 'd7d5', 'a1a3', 'a8b8', 'f1a6', 'c7c6', 'd1e2', 'b7b6', 'd2d4', 'g8h6', 'e1d1', 'c8e6', 'a6b7', 'h6g8', 'a3d3', 'e8d7', 'd3a3', 'h7h6', 'b1c3', 'd7c7', 'e2f1', 'h8h7', 'f1e1', 'b8c8', 'c1f4', 'd8d6', 'f4c1', 'g7g6', 'c1f4', 'h7h8', 'f4e5', 'c8b8', 'e1d2', 'e6f7', 'e5h2', 'd6f4', 'g1f3', 'a7a5', 'f3e1', 'b8d8', 'b7c6', 'd5e4', 'd4d5', 'f7e8', 'd2f4', 'e7e5']
	moves = [Move.from_uci(m) for m in moves]
	for m in moves[:-1] :
		board.make_move(m)
		py_board.push(m)
	fen = board.get_fen()
	passing = fen == py_board.fen()
	print("CORRECT" if passing else "INCORRECT")
	if not passing :
		print(f"\texpected : {py_board.fen()}")
		print(f"\tactual   : {fen}")
	print(py_board)
	
	print(f"-------- {moves[-1].uci()}")
	
	board.make_move(moves[-1])
	py_board.push(moves[-1])
	fen = board.get_fen()
	passing = fen == py_board.fen()
	print(fen)
	print("CORRECT" if passing else "INCORRECT")
	if not passing :
		print(f"\texpected : {py_board.fen()}")
		print(f"\tactual   : {fen}")
		print("---\n---expected\n---")
		print(py_board)
		print("---\n---actual\n---")
		print(PyBoard(fen))
	else :
		print(py_board)
