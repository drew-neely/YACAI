#pragma once

#include <stdint.h>
#include <stdio.h>

/*
	This file contains an array of 781 true random 64 bit unsigned integers to be used for zobrist hashing.
	The numbers are hardcoded here for simplicity and repeatability. These numbers were generated using random.org's 
	atmospheric noise true random number generator. The online form was used to make 3124 integers in the range 
	[1, 65535] (16 bit uints). The hexidecemial representations of these numbers were concattenated together in groups
	of 4 and formatted to fill out the zobrist_randoms array in this file.

	The Zobrist hashing algorithm requires 781 random numbers which represent different attributes of a board state. The
	index in the zobrist random array for a particular attribute may be calculated the following way :
		[0, 767] - represent a particular piece at a particular square
			(square_id * 12) + (((color_type >> 3) - 1) * 6) + piece_type
		768 - represents the side to move is black
		[769, 772] - represent castling rights - order [K, Q, k, q]
		[773-780] - represent en-passant file - order A-H

*/

extern const uint64_t zobrist_randoms[];

// given a square_id and a p_id, returns the zobrist random for that piece at that square
#define zobrist_piece_at(square_id, p_id) (zobrist_randoms[(square_id) * 12 + (((p_id) >> 3) - 1) * 6 + ((p_id) & 0b00111)])

// gives the zobrist random representing its blacks turn to move
#define zobrist_blacks_move (zobrist_randoms[768])

// gives the zobrist random representing a valid castle for the `color type` player on `castle type` side
#define zobrist_castle_avail(color, side) (zobrist_randoms[769 + ((color) >> 2) - (side)])

// gives the zobrist random representing that an enpassant in possible on the given file - inputs [0-7] represent A-H
#define zobrist_enpass_file(file) (zobrist_randoms[773 + (file)])

#define starting_hash (\
	zobrist_piece_at(0 , WHITE | ROOK)   ^ zobrist_piece_at(1,  WHITE | KNIGHT) ^ \
	zobrist_piece_at(2 , WHITE | BISHOP) ^ zobrist_piece_at(3,  WHITE | QUEEN)  ^ \
	zobrist_piece_at(4 , WHITE | KING)   ^ zobrist_piece_at(5,  WHITE | BISHOP) ^ \
	zobrist_piece_at(6 , WHITE | KNIGHT) ^ zobrist_piece_at(7,  WHITE | ROOK)   ^ \
	zobrist_piece_at(8 , WHITE | PAWN)   ^ zobrist_piece_at(9,  WHITE | PAWN)   ^ \
	zobrist_piece_at(10, WHITE | PAWN)   ^ zobrist_piece_at(11, WHITE | PAWN)   ^ \
	zobrist_piece_at(12, WHITE | PAWN)   ^ zobrist_piece_at(13, WHITE | PAWN)   ^ \
	zobrist_piece_at(14, WHITE | PAWN)   ^ zobrist_piece_at(15, WHITE | PAWN)   ^ \
	zobrist_piece_at(48, BLACK | PAWN)   ^ zobrist_piece_at(49, BLACK | PAWN)   ^ \
	zobrist_piece_at(50, BLACK | PAWN)   ^ zobrist_piece_at(51, BLACK | PAWN)   ^ \
	zobrist_piece_at(52, BLACK | PAWN)   ^ zobrist_piece_at(53, BLACK | PAWN)   ^ \
	zobrist_piece_at(54, BLACK | PAWN)   ^ zobrist_piece_at(55, BLACK | PAWN)   ^ \
	zobrist_piece_at(56, BLACK | ROOK)   ^ zobrist_piece_at(57, BLACK | KNIGHT) ^ \
	zobrist_piece_at(58, BLACK | BISHOP) ^ zobrist_piece_at(59, BLACK | QUEEN)  ^ \
	zobrist_piece_at(60, BLACK | KING)   ^ zobrist_piece_at(61, BLACK | BISHOP) ^ \
	zobrist_piece_at(62, BLACK | KNIGHT) ^ zobrist_piece_at(63, BLACK | ROOK)   ^ \
	zobrist_castle_avail(WHITE, CASTLE_KING) ^ zobrist_castle_avail(WHITE, CASTLE_QUEEN) ^ \
	zobrist_castle_avail(BLACK, CASTLE_KING) ^ zobrist_castle_avail(BLACK, CASTLE_QUEEN))
