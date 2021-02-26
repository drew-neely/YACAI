#include <stdint.h>
#include <stdio.h>
#include <vector>
#include <string>

#include "board.h"
#include "move.h"
#include "zobrist.h"

using namespace std;

Board::Board(const char* fen) {
	char* pos = (char*) fen;
	size_t idx;

	// Parse position info
	uint8_t rank = 7;
	uint8_t* square;
	for(square = &squares[63]; square >= squares; ) {
		switch(*pos) {
			case 'P' : *square = WHITE | PAWN   ; square--; break;
			case 'N' : *square = WHITE | KNIGHT ; square--; break;
			case 'B' : *square = WHITE | BISHOP ; square--; break;
			case 'R' : *square = WHITE | ROOK   ; square--; break;
			case 'Q' : *square = WHITE | QUEEN  ; square--; break;
			case 'p' : *square = BLACK | PAWN   ; square--; break;
			case 'n' : *square = BLACK | KNIGHT ; square--; break;
			case 'b' : *square = BLACK | BISHOP ; square--; break;
			case 'r' : *square = BLACK | ROOK   ; square--; break;
			case 'q' : *square = BLACK | QUEEN  ; square--; break;
			case 'K' : *square = WHITE | KING   ; 
					   king_pos(WHITE) = (uint8_t) (square - squares);
					   square--;
					   break;
			case 'k' : *square = BLACK | KING   ;
					   king_pos(BLACK) = (uint8_t) (square - squares);
					   square--;
					   break;
			case '8' : *square = 0; square--;
			case '7' : *square = 0; square--;
			case '6' : *square = 0; square--;
			case '5' : *square = 0; square--;
			case '4' : *square = 0; square--;
			case '3' : *square = 0; square--;
			case '2' : *square = 0; square--;
			case '1' : *square = 0; square--; break;
			case '/' : rank--; break;
			default : assert(false); // unexpected character
		}
		pos++;
	}
	// verify position info
	end_placement :
	assert(rank == 0);
	assert(square == squares - 1);
	pos ++; // consume the space

	// parse turn info
	switch(*pos) {
		case 'w' : turn = WHITE; break;
		case 'b' : turn = BLACK; break;
		default : assert(false);
	}
	pos++; // consume turn character
	assert(*pos == ' '); // expect a space
	pos++; // consume the space

	// parse castiling ability
	*((uint32_t*) castling_avail) = 0; // set all 4 fields of castling_avail to 0 using casting with a biger int
	if(*pos == '-') {
		pos++;
	} else {
		assert(*pos != ' ');
		while(true) {
			switch (*pos) {
				case 'K' : castle_avail(WHITE, CASTLE_KING)  = true; pos++; break;
				case 'Q' : castle_avail(WHITE, CASTLE_QUEEN) = true; pos++; break;
				case 'k' : castle_avail(BLACK, CASTLE_KING)  = true; pos++; break;
				case 'q' : castle_avail(BLACK, CASTLE_QUEEN) = true; pos++; break;
				case ' ' : goto end_castling_ability;
				default : assert(false);
			}
		}
	}
	end_castling_ability:
	assert(*pos == ' '); // expect a space
	pos++; // consume the space
	
	//parse en passant square
	if(*pos == '-') {
		enpass_square = NO_ENPASS;
		pos ++; // consume '-'
	} else {
		assert(*pos >= 'a' && *pos <= 'h'); // expect a file letter
		enpass_square = *pos - 'a'; // add file to enpass square
		pos++; // consume file
		assert(*pos == '3' || *pos == '6'); // expect a 3 or 6 for rank
		enpass_square += (*pos - '1') * 8; // add rank * 8 to complete square_id calculation
		pos ++; // consume rank
	}
	assert(*pos == ' '); // expect a space
	pos++; // consume the space

	// parse half move clock 
	assert(*pos >= '0' && *pos <= '9');
	clock = stoi(pos, &idx);
	pos += idx; // increment pos to end of number
	assert(*pos == ' ');
	pos++;

	// parse fullmove counter (stored in halfmoves for Board)
	assert(*pos >= '0' && *pos <= '9');
	halfmoves = (stoi(pos, &idx) - 1) * 2 + (turn >> 4); // add 1 halfmove if its black's turn - fullmoves are incremented after black
	pos += idx;
	assert(*pos == '\0'); // should have reached end of fen string

	// Generate Zobstist hash and store it - this should be the only place this needs to be sone from scratch
	zobrist = 0;
	for(uint8_t i = 0; i < 64; i++) {
		if(squares[i] != 0) {
			zobrist ^= zobrist_piece_at(i, squares[i]);
		}
	}
	if(turn == BLACK) {
		zobrist ^= zobrist_blacks_move;
	}
	zobrist ^= (castle_avail(WHITE, CASTLE_KING))  ? zobrist_castle_avail(WHITE, CASTLE_KING)  : 0;
	zobrist ^= (castle_avail(WHITE, CASTLE_QUEEN)) ? zobrist_castle_avail(WHITE, CASTLE_QUEEN) : 0;
	zobrist ^= (castle_avail(BLACK, CASTLE_KING))  ? zobrist_castle_avail(BLACK, CASTLE_KING)  : 0;
	zobrist ^= (castle_avail(BLACK, CASTLE_QUEEN)) ? zobrist_castle_avail(BLACK, CASTLE_QUEEN) : 0;
	if(enpass_square != NO_ENPASS) {
		zobrist ^= zobrist_enpass_file(file(enpass_square));
	}
}

// Initializes board to starting position
Board::Board() {
	squares[0] = WHITE | ROOK;
	squares[1] = WHITE | KNIGHT;
	squares[2] = WHITE | BISHOP;
	squares[3] = WHITE | QUEEN;
	squares[4] = WHITE | KING;
	squares[5] = WHITE | BISHOP;
	squares[6] = WHITE | KNIGHT;
	squares[7] = WHITE | ROOK;
	for(uint8_t i = 8; i < 16; i++) {
		squares[i] = WHITE | PAWN;
	}
	for(uint8_t i = 16; i < 48; i++) {
		squares[i] = 0;
	}
	for(uint8_t i = 48; i < 56; i++) {
		squares[i] = BLACK | PAWN;
	}
	squares[56] = BLACK | ROOK;
	squares[57] = BLACK | KNIGHT;
	squares[58] = BLACK | BISHOP;
	squares[59] = BLACK | QUEEN;
	squares[60] = BLACK | KING;
	squares[61] = BLACK | BISHOP;
	squares[62] = BLACK | KNIGHT;
	squares[63] = BLACK | ROOK;

	king_pos[0] = 4;
	king_pos[1] = 60;

	turn = WHITE;
	for(uint8_t i = 0; i < 4; i++) {
		castling_avail[i] = true;
	}

	enpass_square = NO_ENPASS;
	clock = 0;
	halfmoves = 0;

	zobrist = starting_hash;
}

// precondition: move must be a valid move - undefined behavior if not
void Board::makeMove(Move move) {
	Transition trans(move, this);

	// set variables for special moves (enpassant, castling right changes, and promotion)
	uint8_t from_pid = squares[move.from_square];
	uint8_t to_pid = squares[move.to_square];
	
	uint8_t new_enpass_square = NO_ENPASS;
	uint8_t new_to_square_pid = new_to_square_pid = squares[move.from_square];
	uint8_t new_clock = clock + 1;


	if(trans.is_special == TRANSITION_ENPASS) { // enpassant
		new_clock = 0;
		squares[trans.special_info.capture_square_id] = 0;
		goto endUpdate;
	} else if(trans.is_special == TRANSITION_PROMOTE) { // promotion
		new_clock = 0;
		new_to_square_pid = turn | piece(move.promotion_type);
	} else if(trans.is_special == TRANSITION_CASTLE) { // castle
		castle_avail(turn, CASTLE_KING) = false;
		castle_avail(turn, CASTLE_QUEEN) = false;
		switch(turn | trans.special_info.castle_type) {
			case WHITE | CASTLE_QUEEN :
				squares[3] = squares[0];
				squares[0] = 0;
				break;
			case WHITE | CASTLE_KING :
				squares[5] = squares[7];
				squares[7] = 0;
				break;
			case BLACK | CASTLE_QUEEN :
				squares[59] = squares[56];
				squares[56] = 0;
				break;
			case BLACK | CASTLE_KING :
				squares[61] = squares[63];
				squares[63] = 0;
				break;
			default : assert(false);
		}
		goto endUpdate;
	} else if(piece(from_pid) == PAWN) { // pawn move (double push, single push, or normal capture)
		new_clock = 0; // pawn move resets 50 move counter
		uint8_t opposite_pawn = ((turn == WHITE)? BLACK : WHITE) | PAWN;
		bool neighbor_enemy_pawn = (file(move.to_square) != 0 && squares[move.to_square - 1] == opposite_pawn) || // Not on the left of board && enemy pawn to the left
				(file(move.to_square) != 7 && squares[move.to_square + 1] == opposite_pawn); // Not on the right of board && enemy pawn to the right
		if(neighbor_enemy_pawn && rank(move.from_square) == 1 && rank(move.to_square) == 3) { // White double pawn move creating available enpass
			new_enpass_square = move.from_square + 8;
		} else if(neighbor_enemy_pawn && rank(move.from_square) == 6 && rank(move.to_square) == 4) { // Black double pawn move creating available enpass
			new_enpass_square = move.from_square - 8;
		}
		goto endUpdate;
	} else if(piece(from_pid) == KING) { // normal king move
		castle_avail(turn, CASTLE_KING) = false;
		castle_avail(turn, CASTLE_QUEEN) = false;
	}
	
	// Check castling rights by rook moves and captures
	if(move.from_square == 0 || move.to_square == 0) { // white queen rook invalid
		castle_avail(WHITE, CASTLE_QUEEN) = false;
	}
	if(move.from_square == 7 || move.to_square == 7) { // white king rook invalid
		castle_avail(WHITE, CASTLE_KING) = false;
	}
	if(move.from_square == 56 || move.to_square == 56) { // black queen rook invalid
		castle_avail(BLACK, CASTLE_QUEEN) = false;
	}
	if(move.from_square == 63 || move.to_square == 63) { // black king rook invalid
		castle_avail(BLACK, CASTLE_KING) = false;
	}

	endUpdate:

	enpass_square = new_enpass_square;
	squares[move.to_square] = new_to_square_pid;
	squares[move.from_square] = 0;
	if(trans.capture_p_id != 0) {
		new_clock = 0;
	}
	clock = new_clock;
	halfmoves++;
	
	if(turn == WHITE) {
		turn = BLACK;
	} else {
		turn = WHITE;
	}

	// !!!
	// Update zobrist hash
}

// Technically uses x-fen specification (enpass squares are only recorded when enpass is valid move)
const char* Board::get_fen() {
	char* fen = (char*) malloc(100); // longest fen string possible should be 92 bytes
	uint8_t pos = 0;
	uint8_t len;
	// gen position info
	for(int8_t rank = 7; rank >= 0; rank--) {
		uint8_t gap_size = '0';
		for(int8_t file = 0; file < 8; file++) {
			uint8_t square_id = rank*8+file;
			char piece_char;
			if(squares[square_id] != 0) { // piece is present
				if(gap_size > '0') {
					fen[pos++] = gap_size;
					gap_size = '0';
				}
				switch(squares[square_id]) {
					case WHITE | PAWN   : fen[pos++] = 'P'; break;
					case WHITE | KNIGHT : fen[pos++] = 'N'; break;
					case WHITE | BISHOP : fen[pos++] = 'B'; break;
					case WHITE | ROOK   : fen[pos++] = 'R'; break;
					case WHITE | QUEEN  : fen[pos++] = 'Q'; break;
					case WHITE | KING   : fen[pos++] = 'K'; break;
					case BLACK | PAWN   : fen[pos++] = 'p'; break;
					case BLACK | KNIGHT : fen[pos++] = 'n'; break;
					case BLACK | BISHOP : fen[pos++] = 'b'; break;
					case BLACK | ROOK   : fen[pos++] = 'r'; break;
					case BLACK | QUEEN  : fen[pos++] = 'q'; break;
					case BLACK | KING   : fen[pos++] = 'k'; break;
					default : assert(false);
				}
			} else { // no piece here
				gap_size++;
			}
		}
		if(gap_size > '0') {
			fen[pos++] = gap_size;
		}
		if(rank != 0) { 
			fen[pos++] = '/';
		}
	}
	fen[pos++] = ' ';
	
	// gen turn
	switch(turn) {
		case WHITE : fen[pos++] = 'w'; break;
		case BLACK : fen[pos++] = 'b'; break;
		default : assert(false);
	}
	fen[pos++] = ' ';

	// gen castling info
	if(*((uint32_t*) castling_avail) == 0) { // no castling
		fen[pos++] = '-';
	} else { // some castling
		if(castle_avail(WHITE, CASTLE_KING)) {
			fen[pos++] = 'K';
		}
		if(castle_avail(WHITE, CASTLE_QUEEN)) {
			fen[pos++] = 'Q';
		}
		if(castle_avail(BLACK, CASTLE_KING)) {
			fen[pos++] = 'k';
		}
		if(castle_avail(BLACK, CASTLE_QUEEN)) {
			fen[pos++] = 'q';
		}
	}
	fen[pos++] = ' ';

	// gen enpassant square
	if(enpass_square == NO_ENPASS) { // no enpassant
		fen[pos++] = '-';		
	} else {
		fen[pos++] = 'a' + file(enpass_square);
		fen[pos++] = '1' + rank(enpass_square);
	}
	fen[pos++] = ' ';
	
	// gen halfmove clock
	len = sprintf(&fen[pos], "%d", clock);
	assert(len > 0);
	pos += len;
	fen[pos++] = ' ';

	// gen fullmove counter
	len = sprintf(&fen[pos], "%d", halfmoves / 2 + 1);
	assert(len > 0);
	pos += len;

	fen[pos] = '\0';
	return fen;
}