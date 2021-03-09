#pragma once

#include <stdint.h>
#include <stdio.h>
#include <vector>

struct Board;
#include "move.h"

using namespace std;

// piece types
const uint8_t PAWN = 0;
const uint8_t KNIGHT = 1;
const uint8_t BISHOP = 2;
const uint8_t ROOK = 3;
const uint8_t QUEEN = 4;
const uint8_t KING = 5;

// color types
const uint8_t WHITE = 8;
const uint8_t BLACK = 16;

// castle types
const uint8_t CASTLE_QUEEN = 1;
const uint8_t CASTLE_KING = 2;

// other enums
const uint8_t NO_ENPASS = 255;

/*
	A p_id (piece id) is a 5 bit value that is in the form <color>|<piece>
	ie.
		WHITE | KING = 0b01110 // White King
		BLACK | KING = 0b10110 // Black King
		WHITE | PAWN = 0b01001 // White Pawn
*/

#define piece(p_id) ((p_id) & 0b00111) // Gives the piece type of a p_id
#define color(p_id) ((p_id) & 0b11000) // Gives the color type of a p_id

#define rank(square_id) ((square_id) / 8)
#define file(square_id) ((square_id) % 8)
#define square_id(rank, file) ((rank) * 8 + (file))

#define other_color(color) (24 - (color))

// Gives the square_id of the king of specified color
#define king_pos(color) king_pos[((color) >> 3) - 1] 

// Gives boolean representing the ability of the king of given color to castle
// 	on the given side - True does not imply that the castle is valid, simply that
// 	is possible for it to become valid.
#define castle_avail(color, side) castling_avail[((color) >> 2) - (side)]


struct Board {
	uint8_t squares[64]; // array of p_ids or NULL for empty - indecies correstend to squares { 0: A1, 1: B1, ... 7: H1, 8: A2, ... }
	uint8_t king_pos[2]; // [<White>, <Black>]
	uint8_t turn; // WHITE or BLACK
	uint8_t castling_avail[4]; // [<White Kingside>, <White Queenside>, <Black Kingside>, <Black Queenside>]
	uint8_t enpass_square; // square_id of the square to be moved by enpaasant capture (refer to fen encoding) - NO_ENPASS if no enpassant
	uint8_t clock; // set to zero on a capture or pawn move, incremented otherwise - draw if clock == 100
	uint16_t halfmoves; // number of halfmoves since the start of the game
	uint64_t zobrist;
	vector<Transition*> transitions;
	
	Board();
	Board(const char* fen);

	const char* get_fen();

	vector<Move> legal_moves();

	// move is not checked to be legal
	// move not legal => undefined behavior
	void makeMove(Move move);

	Move unmakeMove();

	uint64_t countPositions(uint8_t depth);
	
};