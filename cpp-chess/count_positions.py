from re import search
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
	"r3R3/2N5/2R1n3/KP2k3/3rpr2/8/1Q2RPPB/n3R3 w - - 0 1", # one check
	"N3R3/8/K1R1n3/1P2k3/3rpPr1/8/1Q2R1PB/n3R3 b - - 0 1", # one pawn check, 3 pins
	"4R3/3N4/K3n3/4k3/3rpPr1/8/1Q2R1PB/n3R3 b - - 0 1", # one pawn, one knight check
	"4R3/3Nnn2/K7/4k3/3rpr2/6P1/1Q2R1PB/n3R3 b - - 0 1", # one knight check
	"r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1", # perf 2
	"r3k2r/p1ppqNb1/bn2pnp1/3P4/1p2P3/2N2Q1p/PPPBBPPP/R3K2R b KQkq - 0 1", # perf 2 after e5f7
	"r3k2r/p1ppqpb1/bn2pnp1/3PN3/Pp2P3/2N2Q1p/1PPBBPPP/R3K2R b KQkq a3 0 1" # perf 2 after a2a4
][11]
print(starting_fen)

cpp_board = Board(starting_fen) if starting_fen else Board()
py_board = PyBoard(starting_fen) if starting_fen else PyBoard()

# if __name__ == "__main__" :
# 	print(board.count_positions(1))
# 	exit()

def cpp_search(board, depth) :
	# board = Board(starting_fen) if starting_fen else Board()
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

def find_diff(pyboard, board, depth) :
	moves = list(pyboard.legal_moves)
	for move in moves :
		pyboard.push(move)
		board.make_move(move)
		cpplen = cpp_search(board, depth)
		pylen = py_search(pyboard, depth)
		if(cpplen != pylen) :
			print(f"diff from {move.uci()} in position \"{pyboard.fen()}\"")
			print(f"cpplen = {cpplen}, pylen = {pylen}")
		py_board.pop()
		board.unmake_move()
	
# if __name__ == "__main__" :
# 	find_diff(py_board, cpp_board, 1)
# 	exit()

if __name__ == "__main__" :
	for i in range(1, 6) :
		print(f"----- Depth {i} -----")
		start = time()
		cpp_count = cpp_search(cpp_board, i)
		cpp_time = time() - start
		print(f"cpp   : {cpp_count:8} positions, ({cpp_time:.2}s)")
		start = time()
		py_count = py_search(py_board, i)
		py_time = time() - start
		print(f"python: {py_count:8} positions, ({py_time:.2}s)")
		print()
	# print([m.uci() for m in py_board.legal_moves])

