from time import time

from chess import Board as PyBoard
from cpp_chess import Board

# positions obtained from https://www.chessprogramming.org/Perft_Results
#     these are positions which try to emphasize edge cases

tests = {
	"rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1" : # starting position
		(5, [1, 20, 400, 8902, 197281, 4865609, 119060324,	3195901860, 84998978956, 2439530234167]),
	"r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1" : # position 2
		(4, [1, 48, 2039, 97862, 4085603, 193690690, 8031647685]),
	"8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - - 0 1" : # position 3
		(6, [1, 14, 191, 2812, 43238, 674624, 11030083, 178633661, 3009794393]),
	"r3k2r/Pppp1ppp/1b3nbN/nP6/BBP1P3/q4N2/Pp1P2PP/R2Q1RK1 w kq - 0 1" : # position 4
		(5, [1, 6, 264, 9467, 422333, 15833292, 706045033]),
	"r2q1rk1/pP1p2pp/Q4n2/bbp1p3/Np6/1B3NBn/pPPP1PPP/R3K2R b KQ - 0 1" : # position 4 mirrored
		(5, [1, 6, 264, 9467, 422333, 15833292, 706045033]),
	"rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KQ - 1 8" : # position 5
		(5, [1, 44, 1486, 62379, 2103487, 89941194]),
	"r4rk1/1pp1qppp/p1np1n2/2b1p1B1/2B1P1b1/P1NP1N2/1PP1QPPP/R4RK1 w - - 0 10" : # position 6
		(4, [1, 46, 2079, 89890, 3894594, 164075551, 6923051137, 287188994746]),
}

def py_search(board, depth) :
	moves = board.legal_moves
	if depth == 0 :
		return 1
	if depth == 1 :
		return len(list(moves))
	else :
		count = 0
		for move in moves :
			board.push(move)
			# print(f"move: {move.uci()}")
			count += py_search(board, depth - 1)
			board.pop()
	return count


if __name__ == "__main__" :
	# True for cpp board - false for Python board
	use_cpp_board = False
	print(f"using {'CPP BOARD' if use_cpp_board else 'PYTHON BOARD'}")
	failed = 0
	for test, (max_d, num_leafs) in tests.items() :
		print(f"testing \"{test}\"")
		board = Board(test) if use_cpp_board else PyBoard(test)
		for d, ans in enumerate(num_leafs[:max_d+1]) :
			start = time()
			actual = board.count_positions(d) if use_cpp_board else py_search(board, d)
			total = time() - start
			if actual == ans :
				print(f"depth {d} -> {actual} positions ({round(total, 2)}s)")
			else :
				print(f"depth {d} FAILED ({round(total, 2)}s)")
				print(f"\tactual = {actual}")
				print(f"\texpected = {ans}")
				failed += 1
				break
		print()
	print("--------")
	print(f"passed {len(tests) - failed}/{len(tests)}")
	print("PASSED" if failed == 0 else "FAILED")



