#include <stdio.h>
#include <assert.h>
#include <vector>
#include <string>

#include "../board.h"
#include "../move.h"
#include "../zobrist.h"
#include "../lru_cache.h"

#include "perft-tests.h"

using namespace std;


//////////////////////////////
//////// Test Cases
//////////////////////////////


void run_pert_tests() {
	const PerftTest tests[] = {
		{"rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",                 6, (uint64_t[10]){1, 20, 400,  8902,  197281,  4865609,   119060324,  3195901860, 84998978956, 2439530234167}},
		{"r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1",     5, (uint64_t[7] ){1, 48, 2039, 97862, 4085603, 193690690, 8031647685}},
		{"8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - - 0 1",                                7, (uint64_t[9] ){1, 14, 191,  2812,  43238,   674624,    11030083,   178633661,  3009794393}},
		{"r3k2r/Pppp1ppp/1b3nbN/nP6/BBP1P3/q4N2/Pp1P2PP/R2Q1RK1 w kq - 0 1",         6, (uint64_t[7] ){1, 6,  264,  9467,  422333,  15833292,  706045033}},
		{"rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KQ - 1 8",                5, (uint64_t[6] ){1, 44, 1486, 62379, 2103487, 89941194 }},
		{"r4rk1/1pp1qppp/p1np1n2/2b1p1B1/2B1P1b1/P1NP1N2/1PP1QPPP/R4RK1 w - - 0 10", 5, (uint64_t[8] ){1, 46, 2079, 89890, 3894594, 164075551, 6923051137, 287188994746}},
	};

	int num_passed = 0;
	int num_failed = 0;

	for(int i = 0; i < 6; i++) {
		Board b = Board(tests[i].fen);
		uint64_t num_positions = countPositions(*&b, tests[i].depth);
		bool passed = num_positions == tests[i].result;
		if(passed) {
			printf("PASS test %d: %llu positions\n", i, num_positions);
			num_passed++;
		} else {
			printf("FAIL test %d: expected %llu, actual %llu\n", i, tests[i].result, num_positions);
			num_failed++;
		}
	}

	if(num_failed == 0) {
		printf("TESTS PASSED %d/%d\n", num_passed, num_passed);
	} else {
		printf("TESTS FAILED %d/%d\n", num_passed, num_passed + num_failed);
	}

}


//////////////////////////////
//////// Perft Counting
//////////////////////////////

#define CHECK_ZOBRIST false
#define CHECK_COMPOSITION false

uint64_t num_hits = 0;
uint64_t num_skips = 0;

uint64_t countPositions(Board& board, uint64_t depth, lru_cache<string, uint64_t>& lru) {

	string fen = board.get_fen();
	// printf("%zu :: %s\n", lru.size(), fen.c_str());
	if(lru.contains(fen)) {
		uint64_t count = lru.get(fen);
		num_hits++;
		num_skips += count;
		return count;
	}
	if(CHECK_ZOBRIST && board.state->zobrist != board.genZobrist()) {
		uint64_t current = board.state->zobrist;
		printf("ERROR: Mismatch in zobrist\n");
		printf("Current position:  %s\n", board.get_fen().c_str());
		board.unmakeMove();
		printf("Previous position: %s\n", board.get_fen().c_str());
		printf("diff = %llx\n", current ^ board.state->zobrist ^ zobrist_blacks_move);
		assert(false);
	}
	if(CHECK_COMPOSITION && Composition(*board.state) != board.state->composition) {
		printf("ERROR: Mismatch in composition\n");
		printf("Expected : %llx\n", Composition(*board.state).compositionId);
		printf("Current  : %llx  %s\n", board.state->composition.compositionId, board.get_fen().c_str());
		board.unmakeMove();
		printf("Previous : %llx  %s\n", board.state->composition.compositionId, board.get_fen().c_str());
		assert(false);
	}
	uint64_t count = 0;
	if(depth == 0) {
		return 1;
	} else if(depth == 1) {
		vector<Move> moves = board.legalMoves();
		count = moves.size();
		lru.insert(fen, count);
		return count;
	}
	vector<Move> moves = board.legalMoves();
	for(int i = 0; i < moves.size(); i++) {
		board.makeMove(moves[i]);
		count += countPositions(board, depth - 1, lru);
		board.unmakeMove();
	}
	lru.insert(fen, count);
	return count;
}

uint64_t countPositions(Board& board, uint64_t depth) {

	lru_cache<string, uint64_t> lru(100000000);
	num_hits = 0;
	num_skips = 0;

	uint64_t count = countPositions(board, depth, lru);

	printf("\t num lru hits : %llu , num lru skips : %llu\n", num_hits, num_skips);

	return count;

}