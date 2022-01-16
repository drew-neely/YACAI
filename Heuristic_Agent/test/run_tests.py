import argparse
from test_bench import ArrMinimax, TupMinimax
from test_cases import ArrTestCase, TupleTestCase, TestCase


if __name__ == "__main__" :

	parser = argparse.ArgumentParser(description='Minimax test bench')
	parser.add_argument('-t', '-tests', dest='tests', type = int, action='store', nargs = '*', default=None) # 1 indexed
	parser.add_argument('-np', '-no_prune', dest='prune', action='store_false')
	parser.add_argument('-v', '-verbose', dest='verbose', action='store_true')
	args = parser.parse_args()

	####################################################

	pass_tests = 0
	fail_tests = []
	total_tests = 0
	target_tests = [(t, TestCase.all_tests[t-1]) for t in args.tests] if args.tests else enumerate(TestCase.all_tests)
	for (i, test) in target_tests :
		if args.verbose : print(f"Running test {i+1}\n")

		if isinstance(test, ArrTestCase) :
			minimax = ArrMinimax(test, pruning = args.prune, verbose = args.verbose)
		elif isinstance(test, TupleTestCase) :
			minimax = TupMinimax(test, pruning = args.prune, verbose = args.verbose)

		if test.res is None :
			if args.verbose : print()
			print(f"Test {i+1} unknown (dims={test.depth})")
			print(f"\t")
			print(f"\tactual={minimax.best_quality}")
			print()
			print(f"\tnum_evaled = {minimax.num_evaled}")
			if args.verbose : print("UNKNOWN\n--------------------------")
		elif minimax.best_quality != test.res :
			fail_tests.append(i)
			if args.verbose : print()
			print(f"Failed test {i+1}")
			print(f"\t{test}")
			print(f"\t{'maxing' if test.maxing else 'mining'}")
			print(f"\tactual={minimax.best_quality}")
			print(f"\texpected = {test.res}")
			if args.verbose : print(f"\tnum_evaled = {minimax.num_evaled}")
			if args.verbose : print("FAIL\n--------------------------")
			else : print()
		else :
			pass_tests += 1
			if args.verbose : print(f"\tnum_evaled = {minimax.num_evaled}")
			if args.verbose : print("PASS\n--------------------------")
		total_tests += 1
	if fail_tests and not args.verbose : print("----\n")
	print(f"Ran {total_tests} tests")
	print(f"Passed {pass_tests}/{pass_tests+len(fail_tests)}")
	print(f"{(round(pass_tests/(pass_tests+len(fail_tests))*10000))/100 if pass_tests+len(fail_tests) != 0 else 'nil'}%")

