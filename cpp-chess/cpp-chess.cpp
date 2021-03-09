#include <stdio.h>

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
	assert_valid_bd(bd);
	Move move = {from_square, to_square, promotion_type};
	boardDescriptorTable[bd]->makeMove(move);
}

extern "C" void unmake_move(int bd) {
	assert_valid_bd(bd);
	boardDescriptorTable[bd]->unmakeMove();
}

extern "C" uint64_t count_positions(int bd, uint8_t depth) {
	assert_valid_bd(bd);
	uint64_t res = boardDescriptorTable[bd]->countPositions(depth);
	return res;
}


extern "C" const char* get_fen(int bd) {
	assert_valid_bd(bd);
	return boardDescriptorTable[bd]->get_fen();
}






int main() {
    printf("Hello, world - wait... I'm a library. Why are you executing me? Let me sleep.");
    return 0;
}