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
	assert_valid_bd(bd);
	uint64_t res = boardDescriptorTable[bd]->countPositions(depth);
	return res;
}


extern "C" const char* get_fen(int bd) {
	assert_valid_bd(bd);
	return boardDescriptorTable[bd]->get_fen();
}






int main() {
	// I will count some random positions here for profiling purposes

	const char* fens[6] = {
		"rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
		"r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1",
		"8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - - 0 1",
		"r3k2r/Pppp1ppp/1b3nbN/nP6/BBP1P3/q4N2/Pp1P2PP/R2Q1RK1 w kq - 0 1",
		"rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KQ - 1 8",
		"r4rk1/1pp1qppp/p1np1n2/2b1p1B1/2B1P1b1/P1NP1N2/1PP1QPPP/R4RK1 w - - 0 10"
	};

	const int depths[6] = {6, 5, 7, 6, 5, 5};

	for(int i = 0; i < 6; i++) {
		int bd = create_board_from_fen(fens[i])	;
		uint64_t num_positions = count_positions(bd, depths[i]);
		printf("%d: %llu\n", i, num_positions);
	}


    return 0;
}