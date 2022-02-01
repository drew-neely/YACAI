import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import argparse
import chess

from test_bench import ArrMinimax, TupMinimax
from test_cases import ArrTestCase, TupleTestCase, TestCase
from chess_minimax import ChessMinimax


if __name__ == "__main__" :

	parser = argparse.ArgumentParser(description='Minimax test bench')
	parser.add_argument('-t', '-tests', dest='tests', type = int, action='store', nargs = '*', default=None) # 1 indexed
	parser.add_argument('-np', '-no_prune', dest='prune', action='store_false')
	parser.add_argument('-v', '-verbose', dest='tests_verbose', action='store_true')
	parser.add_argument('-vv', '-vverbose', dest='minimax_verbose', action='store_true')
	args = parser.parse_args()

	####################################################

	pass_tests = 0
	fail_tests = []
	total_tests = 0
	target_tests = [(t-1, TestCase.all_tests[t-1]) for t in args.tests] if args.tests else enumerate(TestCase.all_tests)
	for (i, test) in target_tests :
		if args.tests_verbose : print(f"Running test {i+1}\n")

		chess_minimax = None
		if isinstance(test, ArrTestCase) :
			minimax = ArrMinimax(test, pruning = args.prune, verbose = args.minimax_verbose)
		elif isinstance(test, TupleTestCase) :
			minimax = TupMinimax(test, pruning = args.prune, verbose = args.minimax_verbose, use_score=test.use_score)
			if test.fen : # run a chessminimax with this to confirm
				board = chess.Board(test.fen)
				chess_minimax = ChessMinimax(board, test.depth, color=board.turn, pruning = args.prune, verbose = args.minimax_verbose)

		if test.res is None : # Test is unknown
			if args.tests_verbose : print()
			print(f"Test {i+1} unknown (depth={test.depth}) {'< '+test.fen+' >' if isinstance(test, TupleTestCase) and test.fen else ''}")
			print()
			print(f"\tactual={minimax.best_quality}")
			if chess_minimax :
				print(f"\tchess_actual = {chess_minimax.best_quality}")
				print()
				print(f"\tbest move = {chess_minimax.best_choice}")
				
			print(f"\tnum_evaled = {minimax.num_evaled}")
			print()
			if chess_minimax and chess_minimax.best_quality == minimax.best_quality :
				pass_tests += 1
				print("SOFT PASS\n--------------------------")
			elif chess_minimax and chess_minimax.best_quality != minimax.best_quality :
				fail_tests.append(i)
				print("FAIL \n--------------------------")
			else :
				print("UNKNOWN\n--------------------------")
		elif minimax.best_quality != test.res : # Test Failed
			fail_tests.append(i)
			if args.tests_verbose : print()
			print(f"Failed test {i+1}")
			print(f"\t{test}")
			print(f"\t{'maxing' if test.maxing else 'mining'}")
			print(f"\tactual={minimax.best_quality}")
			print(f"\texpected = {test.res}")
			if args.tests_verbose : print(f"\tnum_evaled = {minimax.num_evaled}")
			if args.tests_verbose : print("FAIL\n--------------------------")
			else : print()
		elif chess_minimax and chess_minimax.best_quality != minimax.best_quality : # test soft-failed
			fail_tests.append(i)
			if args.tests_verbose : print()
			print(f"Soft-Failed test {i+1} : <{test.fen}>")
			print(f"\t{test}")
			print(f"\tactual={minimax.best_quality}")
			print(f"\tchess_actual={chess_minimax.best_quality}")
			print(f"\texpected = {test.res}")
			print()
			print(f"\tbest move = {chess_minimax.best_choice}")
			if args.tests_verbose : print(f"\tnum_evaled = {minimax.num_evaled}")
			if args.tests_verbose : print("FAIL\n--------------------------")
			else : print()
		else : # test passed
			pass_tests += 1
			if args.tests_verbose : print(f"\tnum_evaled = {minimax.num_evaled}")
			if chess_minimax :
				print(f"\tchess_actual = {chess_minimax.best_quality}")
				print(f"\tbest move = {chess_minimax.best_choice}")
			if args.tests_verbose : print("PASS\n--------------------------")

		
		total_tests += 1
	if fail_tests and not args.tests_verbose : print("----\n")
	print(f"Ran {total_tests} tests")
	print(f"Passed {pass_tests}/{pass_tests+len(fail_tests)}")
	print(f"{(round(pass_tests/(pass_tests+len(fail_tests))*10000))/100 if pass_tests+len(fail_tests) != 0 else 'nil'}%")

