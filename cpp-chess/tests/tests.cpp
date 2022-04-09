
#include <stdio.h>
#include <assert.h>

#include "../board.h"
#include "../move.h"
#include "../zobrist.h"
#include "../lru_cache.h"

#include "perft-tests.h"
#include "zobrist-tests.h"
#include "game-end-tests.h"

using namespace std;


int main() {

	auto startTime = clock();//time(nullptr);

	/////////

	run_game_end_tests("./tests/test_database/lichess_db_standard_rated_2013-03.pgn.list");
	run_game_end_tests("./tests/test_database/lichess_db_standard_rated_2014-01.pgn.list");
	run_pert_tests();
	// test_zobrist_conflict();

	/////////
	double elapsedTime = ((double)clock() - startTime) / CLOCKS_PER_SEC;

	printf("Time Elapsed : %.2fs\n", elapsedTime );

    return 0;
}