from cpp_chess import Board, Move
from chess import Board as PyBoard
from time import time

starting_fen = [
	None,
	"8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - - 0 1", # one pin
	"8/2p5/3p4/KP5r/5R1k/8/4P1P1/8 b - - 0 1", # one check - rook
	"8/2p5/3p4/KP5r/5R1k/6P1/4P3/8 b - - 0 1", # two check - rook/pawn
	"4R3/2N5/4n3/KP2k3/5r2/8/1Q2RPPB/n7 b - - 0 1", # two check, two pin
	"4R3/2N5/4n3/KP2k3/3r1r2/4p3/1Q2RPPB/n3R3 b - - 0 1", # 4 pin
	"4R3/2N5/4n3/KP2k3/3rpr2/8/1Q2RPPB/n3R3 w - - 0 1", # nothing
	"r3R3/2N5/2R1n3/KP2k3/3rpr2/8/1Q2RPPB/n3R3 w - - 0 1" # one check
][7]

board = Board(starting_fen) if starting_fen else Board()
py_board = PyBoard(starting_fen) if starting_fen else PyBoard()

if __name__ == "__main__" :
	board.count_positions(1)
	exit()

def cpp_search(board, depth) :
	board = Board(starting_fen) if starting_fen else Board()
	return board.count_positions(depth)

def py_search(board, depth) :
	moves = board.legal_moves
	if depth == 1 :
		return len(list(moves))
	else :
		count = 0
		for move in moves :
			board.push(move)
			count += py_search(board, depth - 1)
			board.pop()
	return count
			

if __name__ == "__main__" :
	for i in range(1, 5) :
		start = time()
		py_count = py_search(py_board, i)
		py_time = time() - start
		start = time()
		cpp_count = cpp_search(py_board, i)
		cpp_time = time() - start
		print(f"----- Depth {i} -----")
		print(f"python: {py_count:8} positions, ({py_time:.2}s)")
		print(f"cpp   : {cpp_count:8} positions, ({cpp_time:.2}s)")
		print()

