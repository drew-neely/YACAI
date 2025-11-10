
#include <stdio.h>
#include <assert.h>

#include "../board.h"
#include "../move.h"
#include "../zobrist.h"
#include "../lru_cache.h"
#include "../minimax.h"

#include "perft-tests.h"
#include "zobrist-tests.h"
#include "game-end-tests.h"
#include "puzzle-tests.h"

using namespace std;

#ifdef TESTING
int main() {

	auto startTime = clock();//time(nullptr);

	/////////

	run_game_end_tests("./tests/test_database/lichess_db_standard_rated_2013-03.pgn.list");
	run_game_end_tests("./tests/test_database/lichess_db_standard_rated_2014-01.pgn.list");
	// run_game_end_tests("./tests/test_database/lichess_db_standard_rated_2018-03.pgn.list");
	// run_game_end_tests("./tests/test_database/lichess_db_standard_rated_2019-10.pgn.list");
	// run_game_end_tests("./tests/test_database/fail.list");
	run_pert_tests();
	// test_zobrist_conflict();
	// run_puzzle_tests("./tests/puzzle_tests/puzzles.list");

	/////////
	double elapsedTime = ((double)clock() - startTime) / CLOCKS_PER_SEC;

	printf("Time Elapsed : %.2fs\n", elapsedTime );

    return 0;
}
#endif