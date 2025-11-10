#include <assert.h>
#include <stdio.h>
#include <cstdlib>
#include <cstring>
#include <string>

#include "board.h"
#include "move.h"
#include "tests/perft-tests.h"
// #include "zobrist.h"

#define DESCRIPTOR_TABLE_SIZE 100

Board* boardDescriptorTable[DESCRIPTOR_TABLE_SIZE]; // NULL = not allocated

#define assert_valid_bd(bd) \
	assert((bd) >= 0 && (bd) < DESCRIPTOR_TABLE_SIZE); \
	assert(boardDescriptorTable[(bd)] != NULL)

extern "C" int test_func() {
	// printf("got string \"%s\"\n", str);
	return 0;
}
extern "C" void test_func2(int a) {
	// printf("got string \"%s\"\n", str);
	return;
}

extern "C" int create_board() {
	for(int i = 0; i < DESCRIPTOR_TABLE_SIZE; i++) {
		if(boardDescriptorTable[i] == NULL) {
			boardDescriptorTable[i] = new Board();
			return i;
		}
	}
	return -1; // No free boards
}

extern "C" int create_board_from_fen(const char* fen) {
	for(int i = 0; i < DESCRIPTOR_TABLE_SIZE; i++) {
		if(boardDescriptorTable[i] == NULL) {
			boardDescriptorTable[i] = new Board(fen);
			return i;
		}
	}
	return -1; // No free boards
}

extern "C" void free_board(int bd) {
	assert_valid_bd(bd);
	delete boardDescriptorTable[bd];
	boardDescriptorTable[bd] = NULL;
}

extern "C" void make_move(int bd, const char* uci_move) {
	assert_valid_bd(bd);
	assert(uci_move != NULL);
	Board* board = boardDescriptorTable[bd];
	Move move(std::string(uci_move), *board);
	board->makeMove(move);
}

extern "C" void unmake_move(int bd) {
	assert_valid_bd(bd);
	boardDescriptorTable[bd]->unmakeMove();
}

extern "C" int count_positions(int bd, uint8_t depth) {
	// assert(false);
	assert_valid_bd(bd);
	uint64_t res = countPositionsZobristTransTable(*boardDescriptorTable[bd], depth);
	// uint64_t res = boardDescriptorTable[bd]->countPositions(depth);
	return res;
}


extern "C" char* get_fen(int bd) {
	// assert(false);
	assert_valid_bd(bd);
	std::string fen = boardDescriptorTable[bd]->get_fen();
	size_t length = fen.size() + 1;
	char* buffer = static_cast<char*>(std::malloc(length));
	if(buffer == NULL) {
		return NULL;
	}
	std::memcpy(buffer, fen.c_str(), length);
	return buffer;
}


// If compiling as a standalone library include a stub entry point
#ifndef TESTING
int main() {
	printf("This is a library - not an executable\n");
}
#endif
