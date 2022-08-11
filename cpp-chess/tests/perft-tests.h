#pragma once

#include <stdio.h>
#include <assert.h>
#include <map>

#include "../board.h"
#include "../move.h"
#include "../zobrist.h"
#include "../lru_cache.h"

using namespace std;

struct PerftTest {

	PerftTest(const char* fen, uint64_t depth, const uint64_t* results) : fen(fen), result(results[depth]), depth(depth) {}

	const char* fen;
	uint64_t depth; 
	uint64_t result;

};


///////////

#define PERFT_NO_TRANSPOSITION 0
#define PERFT_FEN_TRANSPOSITION 1
#define PERFT_ZOBRIST_TRANSPOSITION 2

#define PERFT_FUNCTION 2 // pick a perft function for run_perft_tests to use

void run_pert_tests();


///////////

// enable/disable functional checks
#define CHECK_ZOBRIST false
#define CHECK_COMPOSITION false

const size_t lru_capacity = 100000000;

uint64_t countPositions(Board& board, uint64_t depth); // Counts positions achievable at depth from board

uint64_t countPositionsFenLru(Board& board, uint64_t depth); // Uses an LRU transposition table keyed on the fen of the board

uint64_t countPositionsZobristTransTable(Board& board, uint64_t depth); // Uses an LRU transposition table keyed on the zobrist hash of the board

