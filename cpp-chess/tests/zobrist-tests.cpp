
#include <stdio.h>
#include <assert.h>
#include <algorithm>
#include <string>
#include <vector>
#include <map>

#include "../board.h"
#include "../move.h"
#include "../zobrist.h"
#include "../lru_cache.h"

#include "zobrist-tests.h"

using namespace std;

void find_zobrist_conflict(Board& board, uint64_t depth, map<uint64_t, vector<BoardState>>& hashPairs, set<uint64_t>& collisionKeys) {
	const uint64_t zobrist = board.state->zobrist;

	// add current board
	if(hashPairs.count(zobrist)) {
		// see if board already exists in hashPairs
		vector<BoardState>& collisions = hashPairs[zobrist];
		bool found = find(collisions.begin(), collisions.end(), *board.state) != collisions.end();
		if(!found) {
			collisions.push_back(*board.state);
			collisionKeys.insert(zobrist);
		}
	} else {
		vector<BoardState> stateVec = { *board.state };
		hashPairs.insert({zobrist, stateVec});
	}

	// recurse
	if(depth != 0) {
		MoveList moves = board.legalMoves();
		for (Move m : moves) {
			board.makeMove(m);
			find_zobrist_conflict(board, depth - 1, hashPairs, collisionKeys);
			board.unmakeMove();
		}
	}

}


map<uint64_t, vector<BoardState>> find_zobrist_conflict(Board& board, uint64_t depth) {
	map<uint64_t, vector<BoardState>> hashPairs;
	set<uint64_t> collisionKeys;
	find_zobrist_conflict(board, depth, *&hashPairs, *&collisionKeys);
	printf("\tnumber of unique zobrist values = %lu\n", hashPairs.size());
	map<uint64_t, vector<BoardState>> collistionPairs;
	for(uint64_t zobrist : collisionKeys) {
		collistionPairs.insert({zobrist, hashPairs[zobrist]});
	}
	return collistionPairs;
}

void test_zobrist_conflict() {
	vector<ZobristTest> fens = {
		{"rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",                 5},
		{"r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1",     4},
		{"8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - - 0 1",                                6},
		{"r3k2r/Pppp1ppp/1b3nbN/nP6/BBP1P3/q4N2/Pp1P2PP/R2Q1RK1 w kq - 0 1",         5},
		{"rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KQ - 1 8",                4},
		{"r4rk1/1pp1qppp/p1np1n2/2b1p1B1/2B1P1b1/P1NP1N2/1PP1QPPP/R4RK1 w - - 0 10", 4},
	};

	for(ZobristTest test : fens) {
		printf("searching depth = %llu, fen = %s\n", test.depth, test.fen.c_str());
		Board board(test.fen);
		map<uint64_t, vector<BoardState>> collisionPairs = find_zobrist_conflict(*&board, test.depth);
		if(collisionPairs.empty()) {
			printf("\t0 collisions found\n");
		} else {
			for(auto const& [zobrist, collisions] : collisionPairs) {
				printf("\tcollisions on %llx:\n", zobrist);
				for(BoardState state : collisions) {
					printf("\t\t%s\n", Board(state).get_fen().c_str());
				}
			}
		}
		printf("\n");
	}
	
}
