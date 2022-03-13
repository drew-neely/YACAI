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

	PerftTest(const char* fen, uint64_t depth, uint64_t* results) : fen(fen), result(results[depth]), depth(depth) {}

	const char* fen;
	uint64_t depth; 
	uint64_t result;

};

void run_pert_tests();

uint64_t countPositions(Board& board, uint64_t depth); // Function to count the number of positions achievable at a depth from the given board