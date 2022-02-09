#pragma once

#include <vector>
#include <stdint.h>
#include <stdio.h>
#include <string>

struct Move;
#include "board.h"

using namespace std;

#define MOVE_NORMAL 0
#define MOVE_CASTLE 1
#define MOVE_ENPASS 2
#define MOVE_PROMOTE 3

struct Move {
	uint8_t from_square;
	uint8_t to_square;
	uint8_t move_type;
	union {
		uint8_t castle_direction; // stores one of CASTLE_KING or CASTLE_QUEEN
		uint8_t enpass_capture_square; // stores the square_id of the pawn being captured in case of enpass
		uint8_t promotion_type; // stores the piece type in case of promotion
		uint8_t _special_val; // used only for initialization
	};

	// construct normal move
	Move(uint8_t from, uint8_t to) :
		from_square(from), to_square(to), move_type(MOVE_NORMAL) {}

	// construct special move
	Move(uint8_t from, uint8_t to, uint8_t type, uint8_t special) : 
		from_square(from), to_square(to), move_type(type), _special_val(special) {}

	void print() {
		const char* type_str[4] = {"NORMAL", "CASTLE", "ENPASS", "PROMOTE"} ;
		if(move_type  == MOVE_NORMAL) printf("<Move %s-%s>\n", square_names[from_square], square_names[to_square]);
		else printf("<Move %s-%s (%s, %d)>\n", square_names[from_square], square_names[to_square], type_str[move_type], _special_val);
	}
};