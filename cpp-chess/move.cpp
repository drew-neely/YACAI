
#include <vector>
#include <stdint.h>
#include <stdio.h>

#include "move.h"
#include "board.h"

// precondition: move is legal
Transition::Transition(Move move, Board* board) : move(move) {
	// copy prev data and init other fields to 0
	is_special = TRANSITION_NORMAL;
	capture_p_id = 0;
	*((uint32_t*)&castling_avail) = *((uint32_t*)&board->castling_avail); // copy castling rights
	enpass_square = board->enpass_square; 
	clock = board->clock;
	zobrist = board->zobrist;

	// derive transition data
	uint8_t from_pid = board->squares[move.from_square];
	uint8_t to_pid = board->squares[move.to_square];

	if(piece(from_pid) == PAWN) { // pawn move
		if(move.to_square == board->enpass_square) { // En passant capture
			is_special = TRANSITION_ENPASS;
			uint8_t target_index = board->enpass_square + ((rank(enpass_square) == 2)? 8 : -8);
			capture_p_id = board->squares[target_index];
			special_info.capture_square_id = target_index;
		} else if(rank(move.to_square) == 7 || rank(move.to_square) == 0) { // promotion 
			is_special = TRANSITION_PROMOTE;	
		}
	} else if(piece(from_pid) == KING) { // King move
		if(color(from_pid) == WHITE) {
			if(move.from_square == 4) {
				if(move.to_square == 2) { // White queenside castle
					is_special = TRANSITION_CASTLE;
					special_info.castle_type = CASTLE_QUEEN;
				}
				else if(move.to_square == 6) { // White kingside castle
					is_special = TRANSITION_CASTLE;
					special_info.castle_type = CASTLE_KING;
				}
			}
		} else if(color(from_pid) == BLACK) {
			if(move.from_square == 60) {
				if(move.to_square == 58) { // BLACK queenside castle
					is_special = TRANSITION_CASTLE;
					special_info.castle_type = CASTLE_QUEEN;
				}
				else if(move.to_square == 62) { // BLACK kingside castle
					is_special = TRANSITION_CASTLE;
					special_info.castle_type = CASTLE_KING;
				}
			}
		} 
	}

	if(is_special == TRANSITION_NORMAL || is_special == TRANSITION_PROMOTE) { // normal Capture is possible
		capture_p_id = board->squares[move.to_square];
		special_info.capture_square_id = move.to_square;
	}
}