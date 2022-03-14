
#include <stdio.h>
#include <assert.h>

#include "../board.h"
#include "../move.h"
#include "../zobrist.h"
#include "../lru_cache.h"

#include "perft-tests.h"
#include "zobrist-tests.h"

using namespace std;


int main() {

	auto startTime = clock();//time(nullptr);

	/////////

	// run_pert_tests();
	test_zobrist_conflict();

	/////////
	double elapsedTime = ((double)clock() - startTime) / CLOCKS_PER_SEC;

	printf("Time Elapsed : %.2fs\n", elapsedTime );

    return 0;
}