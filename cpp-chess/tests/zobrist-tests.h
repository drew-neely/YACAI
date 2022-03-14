
#include <stdio.h>
#include <assert.h>
#include <string>


#include "../board.h"
#include "../move.h"
#include "../zobrist.h"
#include "../lru_cache.h"

using namespace std;

struct ZobristTest {

	ZobristTest(string fen, uint64_t depth) : fen(fen), depth(depth) {}

	string fen;
	uint64_t depth; 
};

map<uint64_t, vector<BoardState>> find_zobrist_conflict(Board& board, uint64_t depth);

void test_zobrist_conflict();
