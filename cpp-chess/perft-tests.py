from time import time

from chess import Board as PyBoard
from cpp_chess import Board
from statistics import mean
from hashlib import blake2b as hasher

# positions obtained from https://www.chessprogramming.org/Perft_Results
#     these are positions which try to emphasize edge cases

tests = {
	"rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1" : # starting position
		(6, [1, 20, 400, 8902, 197281, 4865609, 119060324,	3195901860, 84998978956, 2439530234167]),
	"r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1" : # position 2
		(5, [1, 48, 2039, 97862, 4085603, 193690690, 8031647685]),
	"8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - - 0 1" : # position 3
		(7, [1, 14, 191, 2812, 43238, 674624, 11030083, 178633661, 3009794393]),
	"r3k2r/Pppp1ppp/1b3nbN/nP6/BBP1P3/q4N2/Pp1P2PP/R2Q1RK1 w kq - 0 1" : # position 4
		(6, [1, 6, 264, 9467, 422333, 15833292, 706045033]),
	"r2q1rk1/pP1p2pp/Q4n2/bbp1p3/Np6/1B3NBn/pPPP1PPP/R3K2R b KQ - 0 1" : # position 4 mirrored
		(6, [1, 6, 264, 9467, 422333, 15833292, 706045033]),
	"rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KQ - 1 8" : # position 5
		(5, [1, 44, 1486, 62379, 2103487, 89941194]),
	"r4rk1/1pp1qppp/p1np1n2/2b1p1B1/2B1P1b1/P1NP1N2/1PP1QPPP/R4RK1 w - - 0 10" : # position 6
		(5, [1, 46, 2079, 89890, 3894594, 164075551, 6923051137, 287188994746]),
}

def hash_tests() :
	hash_num = hasher(digest_size=3)
	pairs = [(fen, d) for (fen, (d, _)) in tests.items()]
	pairs.sort(key=lambda x: x[0]) # alphabetic sort to gurantee order
	for (fen, d) in pairs :
		hash_num.update(f"{fen.strip()} {d}".encode('utf-8'))
	return hash_num.hexdigest()


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


def pretty_print_tests() :
	# True for cpp board - false for Python board
	use_cpp_board = True
	print(f"using {'CPP BOARD' if use_cpp_board else 'PYTHON BOARD'}")
	times = [None] * len(tests)
	failed = 0
	for i, (test, (max_d, num_leafs)) in enumerate(tests.items()) :
		print(f"testing \"{test}\"")
		board = Board(test) if use_cpp_board else PyBoard(test)
		for d, ans in enumerate(num_leafs[:max_d+1]) :
			start = time()
			actual = board.count_positions(d) if use_cpp_board else py_search(board, d)
			total = time() - start
			times[i] = total
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
	if failed == 0 :
		print(f"perf-score = {round(mean(times), 2)}s (average run-time) ")
		print()
	else :
		print("FAILED")

def get_perf_score(n = 10) :
	# True for cpp board - false for Python board
	use_cpp_board = True
	print(f"using {'CPP BOARD' if use_cpp_board else 'PYTHON BOARD'}")
	run_times = []
	for run in range(n) :
		s = 0
		for test, (max_d, num_leafs) in tests.items() :
			board = Board(test) if use_cpp_board else PyBoard(test)
			start = time()
			actual = board.count_positions(max_d) if use_cpp_board else py_search(board, max_d)
			total = time() - start
			assert actual == num_leafs[max_d], f"FAILED: <{test}>, {actual} != {num_leafs[max_d]}"
			s += total
		print(f"run {run} time = {round(s,2)}s")
		run_times.append(s)
	print("discarding first run")
	score = mean(run_times[1:])
	print(f"Score = {round(score, 2)} (test hash: {hash_tests()})")
			
if __name__ == "__main__" :
	# get_perf_score()
	pretty_print_tests()