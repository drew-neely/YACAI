#include <stdint.h>
#include <stdio.h>
#include <vector>
#include <string>

#include "board.h"
#include "attack-squares.h"

using namespace std;

Move::Move(string uci) {
	assert(uci.size() == 4 || (uci.size() == 5 && 
			(uci[4] == 'q' || uci[4] == 'r' ||
			uci[4] == 'n' || uci[4] == 'b')));
	assert(uci[0] >= 'a' && uci[0] <= 'h');
	assert(uci[1] >= '1' && uci[1] <= '8');
	assert(uci[2] >= 'a' && uci[2] <= 'h');
	assert(uci[3] >= '1' && uci[3] <= '8');

	from_square = (uci[0] - 'a') + (uci[1] - '1') * 8;
	to_square   = (uci[2] - 'a') + (uci[3] - '1') * 8;
	
	if(uci.size() == 5) { // Move is promotion
		move_type = MOVE_PROMOTE;
		if     (uci[4] == 'q') promotion_type = QUEEN;
		else if(uci[4] == 'r') promotion_type = ROOK;
		else if(uci[4] == 'b') promotion_type = BISHOP;
		else if(uci[4] == 'n') promotion_type = KNIGHT;
	} else { // Move type cannot be determined without context
		move_type = MOVE_NO_CONTEXT;
	}
}

void Move::build_context(Board& board) {
	
	// check if context already exists
	if(move_type != MOVE_NO_CONTEXT) {
		return;
	}

	// check if castle
	if(from_square == 4 && to_square == 2 && board.castle_avail(WHITE, CASTLE_QUEEN)) { // Castle white Queenside
		move_type = MOVE_CASTLE;
		castle_direction = CASTLE_QUEEN;
		return;
	} else if(from_square == 4 && to_square == 6 && board.castle_avail(WHITE, CASTLE_KING)) { // Castle white Kingside
		move_type = MOVE_CASTLE;
		castle_direction = CASTLE_KING;
		return;
	} else if(from_square == 60 && to_square == 58 && board.castle_avail(BLACK, CASTLE_QUEEN)) { // Castle black Queenside
		move_type = MOVE_CASTLE;
		castle_direction = CASTLE_QUEEN;
		return;
	} else if(from_square == 60 && to_square == 62 && board.castle_avail(BLACK, CASTLE_KING)) { // Castle black Kingside
		move_type = MOVE_CASTLE;
		castle_direction = CASTLE_KING;
		return;
	}

	// check if enpassant 
	if(piece(board.state->squares[from_square]) == PAWN && board.state->enpass_info != NO_ENPASS && to_square == enpass_square(board.state->enpass_info)) {
		move_type = MOVE_ENPASS;
		enpass_capture_square = enpass_capture_square(enpass_square(board.state->enpass_info));
		return;
	}

	// Not a special move type
	move_type = MOVE_NORMAL;
}