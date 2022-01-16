#pragma once

#include <vector>
#include <stdint.h>
#include <stdio.h>

struct Move;
struct Transition;
#include "board.h"
using namespace std;

struct Move {
	uint8_t from_square;
	uint8_t to_square;
	uint8_t promotion_type; // Value not used if the move isn't a promotion
	Move(uint8_t from, uint8_t to) : 
		from_square(from), to_square(to), promotion_type(0) {}
	Move(uint8_t from, uint8_t to, uint8_t prom) : 
		from_square(from), to_square(to), promotion_type(prom) {}
};


#define TRANSITION_NORMAL 0
#define TRANSITION_CASTLE 1
#define TRANSITION_ENPASS 2
#define TRANSITION_PROMOTE 3

/*
	Contains all the information needed to revert a board to its previous state
	Contains extra information which may be inferable, but which speeds up the revert
*/
struct Transition {
	Move move; // The move made to exit the previous state
	uint8_t is_special; // One of TRANSITION_{NORMAL, CASTLE, ENPASS, or PROMOTE}
	uint8_t capture_p_id; // the p_id of the captured piece - 0 if no capture
	union { // only 1 of these will ever be usable at a time
		uint8_t capture_square_id; // (capture_p_id != 0) the square_id from which a piece was captured
		uint8_t castle_type; // (is_special == TRANSITION_CASTLE) the castle type performed
	} special_info;
	uint8_t castling_avail[4]; // the previous value of castling_avail
	uint8_t enpass_square; // the previous value of enpass_square
	uint8_t clock; // The previous value of the clock
	uint64_t zobrist; // The previous zobrist hash

	// precondition: move is legal
	Transition(Move move, Board* board);
};

#define is_special(transition)