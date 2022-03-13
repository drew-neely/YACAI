#pragma once

#include <stdint.h>
#include <stdio.h>
#include <vector>
#include <set>
#include <map>

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

// square color types
const uint8_t LIGHT_SQUARE = 1;
const uint8_t DARK_SQUARE = 0;
const uint8_t NULL_SQUARE = 2;

// castle types
const uint8_t CASTLE_QUEEN = 1;
const uint8_t CASTLE_KING = 2;

// other enums
const uint8_t NO_ENPASS = 255;

// game end reasons
const uint8_t DRAW = 0; // DRAW is not to be used as a game end reason, but as a winner enum in addition to WHITE and BLACK
	// no game end
const uint8_t NO_GAME_END = 0;
	// wins
const uint8_t CHECKMATE   = 0; // WHITE | CHECKMATE   => white win by checkmate,   BLACK | CHECKMATE   => black win by checkmate
const uint8_t TIMEOUT     = 1; // WHITE | TIMEOUT     => white win by timeout,     BLACK | TIMEOUT     => black win by timeout
const uint8_t RESIGNATION = 2; // WHITE | RESIGNATION => white win by resignation, BLACK | RESIGNATION => black win by resignation
	// draws
const uint8_t STALEMATE            = 3;
const uint8_t REPITION             = 4;
const uint8_t FIFTY_MOVE           = 5;
const uint8_t INSUFICIENT_MATERIAL = 6;
const uint8_t AGREEMENT            = 7;


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
#define square_color(square_id) ((((square_id) >> 3) ^ (square_id)) & 1)

#define other_color(color) (24 - (color))

#define square_name(square_id) (square_names[square_id])

// Gives the square_id of the king of specified color
#define king_pos(color) (state->king_pos[((color) >> 3) - 1])

// Gives boolean representing the ability of the king of given color to castle
// 	on the given side - True does not imply that the castle is valid, simply that
// 	is possible for it to become valid.
#define castle_avail(color, side) (state->castling_avail[((color) >> 2) - (side)])

// Sets the castling availability to false while updating the zobrist hash
#define disable_castle(color, side) {                        \
	if(castle_avail((color), (side))) {                          \
		castle_avail((color), (side)) = false;                   \
		state->zobrist ^= zobrist_castle_avail((color), (side)); \
	}}

// performs move while updating the zobrist hash
// Used when move.move_type == MOVE_NORMAL
#define move_piece_check_capture(move) {                                                        \
		if(state->squares[move.to_square] != 0) {                                               \
			state->zobrist ^= zobrist_piece_at((move).to_square, state->squares[(move).to_square]); \
		}                                                                                       \
		state->zobrist ^= zobrist_piece_at((move).from_square, state->squares[(move).from_square])  \
					   ^  zobrist_piece_at((move).to_square, state->squares[(move).from_square]);   \
		state->squares[(move).to_square] = state->squares[(move).from_square];                      \
		state->squares[(move).from_square] = 0;                                                   \
	}

// performs move while updating the zobrist hash
// Should only be used when a capture is impossible or handled seperately
#define move_piece_no_capture(move) {                                                          \
		state->zobrist ^= zobrist_piece_at((move).from_square, state->squares[(move).from_square]) \
					   ^  zobrist_piece_at((move).to_square, state->squares[(move).from_square]);  \
		state->squares[(move).to_square] = state->squares[(move).from_square];                     \
		state->squares[(move).from_square] = 0;                                                  \
	}

/*
	An end_code is a 5 bit value that is in the form <winner>|<reason>
	The winner may be one of WHITE, BLACK, or DRAW
	The reasons [CHECKMATE, TIMEOUT, RESIGNATION] must have either WHITE or BLACK as the winner
	The reasons [STALEMATE, REPITITION, FIFTY_MOVE, INSUFICIENT_MATERIAL, AGREEMENT] must have DRAW as the winner
	Any combination of winner and reason not listed above is an invalid end_code and may have undefined behavior
	ie.
		WHITE | CHECKMATE               // white win by checkmate
		BLACK | RESIGNATION             // black win by resignation
		DRAW  | STALEMATE = STALEMATE   // draw by stalemate
		DRAW  | FIFTY_MOVE = FIFTY_MOVE // draw by fifty move rule
*/
#define winner(end_code)   ((end_code) & 0b11000)
#define reason(end_code)   ((end_code) & 0b00111)
#define game_end(end_code) ((end_code) != 0)
#define draw(end_code)     (((end_code) & 0b11000) == 0)



extern const char* square_names[64];
struct BoardState;
struct Board;

#include "move.h"
#include "chess_containers.h"


struct BoardState {
	uint8_t squares[64]; // array of p_ids or NULL for empty - indecies correstend to squares { 0: A1, 1: B1, ... 7: H1, 8: A2, ... }
	uint8_t king_pos[2]; // [<White>, <Black>]
	uint8_t turn; // WHITE or BLACK
	uint8_t castling_avail[4]; // [<White Kingside>, <White Queenside>, <Black Kingside>, <Black Queenside>]
	uint8_t enpass_square; // square_id of the square to be moved by enpaasant capture (refer to fen encoding) - NO_ENPASS if no enpassant
	uint8_t clock; // set to zero on a capture or pawn move, incremented otherwise - draw if clock == 100
	uint16_t halfmoves; // number of halfmoves since the start of the game
	uint64_t zobrist; // current zobrist hash
	Composition composition; // current set and counts of pices on the board
	uint8_t game_end_reason;

	// Methods

	bool operator==(BoardState& other) const; // determine equality in terms of three-fold repitition rule
};

struct Board {

	BoardState* state;
	vector<BoardState> stateStack;
	
	// Methods

	Board();
	Board(const char* fen);


	void attackSquares(SquareSet& attack_squares, uint8_t color, SquareSet& check_path_end);
	void checksAndPins(SquareSet& check_path, bool& check, bool& double_check,
				map<uint8_t, SquareSet >& pinned_squares);
	vector<Move> legalMoves();

	bool isDrawRepitition();
	bool isDrawFiftyMove();
	bool isDrawInsuficientMaterial();

	// move is not checked to be legal
	// move not legal => undefined behavior
	void makeMove(Move move);

	void unmakeMove();

	string get_fen();
	uint64_t genZobrist();

};