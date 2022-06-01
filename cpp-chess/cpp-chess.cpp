#include <stdio.h>
#include <assert.h>

#include "board.h"
#include "move.h"
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

extern "C" void make_move(int bd, uint8_t from_square, uint8_t to_square, uint8_t promotion_type) {
	assert(false);
	// assert_valid_bd(bd);
	// Move move = Move(from_square, to_square, promotion_type);
	// boardDescriptorTable[bd]->makeMove(move);
}

extern "C" void unmake_move(int bd) {
	assert_valid_bd(bd);
	boardDescriptorTable[bd]->unmakeMove();
}

extern "C" uint64_t count_positions(int bd, uint8_t depth) {
	assert(false);
	// assert_valid_bd(bd);
	// uint64_t res = boardDescriptorTable[bd]->countPositions(depth);
	// return res;
}


extern "C" const char* get_fen(int bd) {
	assert(false);
	// assert_valid_bd(bd);
	// return boardDescriptorTable[bd]->get_fen().c_str();
}


// If compiling as a standalone library include a stub entry point
#ifndef TESTING
int main() {
	printf("This is a library - not an executable\n");
}
#endif