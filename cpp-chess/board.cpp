#include <stdint.h>
#include <stdio.h>
#include <assert.h>
#include <vector>
#include <string>
#include <map>
#define _contains(setmap, key) ((setmap).find(key) != (setmap).end())

#include "board.h"
#include "move.h"
#include "attack-squares.h"
#include "zobrist.h"
#include "square-set.h"

using namespace std;

#define STATE_STACK_STARTING_SIZE 128

const char* square_names[64] = {
	"a1", "b1", "c1", "d1", "e1", "f1", "g1", "h1", 
	"a2", "b2", "c2", "d2", "e2", "f2", "g2", "h2", 
	"a3", "b3", "c3", "d3", "e3", "f3", "g3", "h3", 
	"a4", "b4", "c4", "d4", "e4", "f4", "g4", "h4", 
	"a5", "b5", "c5", "d5", "e5", "f5", "g5", "h5", 
	"a6", "b6", "c6", "d6", "e6", "f6", "g6", "h6", 
	"a7", "b7", "c7", "d7", "e7", "f7", "g7", "h7", 
	"a8", "b8", "c8", "d8", "e8", "f8", "g8", "h8"
};

Board::Board(const char* fen) {

	// initialize stateStack vector
	stateStack.reserve(STATE_STACK_STARTING_SIZE);
	stateStack.emplace_back();
	state = stateStack.data();

	char* pos = (char*) fen;
	size_t idx;
	
	// Parse position info
	uint8_t rank = 7;
	uint8_t* square;
	for(square = &state->squares[56]; square >= state->squares && rank >= 0; ) {
	// for(square = &state->squares[63]; square >= state->squares; ) {
		switch(*pos) {
			case 'P' : *square = WHITE | PAWN   ; square++; break;
			case 'N' : *square = WHITE | KNIGHT ; square++; break;
			case 'B' : *square = WHITE | BISHOP ; square++; break;
			case 'R' : *square = WHITE | ROOK   ; square++; break;
			case 'Q' : *square = WHITE | QUEEN  ; square++; break;
			case 'p' : *square = BLACK | PAWN   ; square++; break;
			case 'n' : *square = BLACK | KNIGHT ; square++; break;
			case 'b' : *square = BLACK | BISHOP ; square++; break;
			case 'r' : *square = BLACK | ROOK   ; square++; break;
			case 'q' : *square = BLACK | QUEEN  ; square++; break;
			case 'K' : *square = WHITE | KING   ; 
					   king_pos(WHITE) = (uint8_t) (square - state->squares);
					   square++;
					   break;
			case 'k' : *square = BLACK | KING   ;
					   king_pos(BLACK) = (uint8_t) (square - state->squares);
					   square++;
					   break;
			case '8' : *square = 0; square++;
			case '7' : *square = 0; square++;
			case '6' : *square = 0; square++;
			case '5' : *square = 0; square++;
			case '4' : *square = 0; square++;
			case '3' : *square = 0; square++;
			case '2' : *square = 0; square++;
			case '1' : *square = 0; square++; break;
			case '/' : rank--; square -= 16; break;
			case ' ' : goto end_placement;
			default : assert(false); // unexpected character
		}
		pos++;
	}
	// verify position info
	end_placement :
	assert(rank == 0);
	pos ++; // consume the space

	// parse turn info
	switch(*pos) {
		case 'w' : state->turn = WHITE; break;
		case 'b' : state->turn = BLACK; break;
		default : assert(false);
	}
	pos++; // consume turn character
	assert(*pos == ' '); // expect a space
	pos++; // consume the space

	// parse castiling ability
	*((uint32_t*) state->castling_avail) = 0; // set all 4 fields of state->castling_avail to 0 using casting with a bigger int
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
		state->enpass_square = NO_ENPASS;
		pos ++; // consume '-'
	} else {
		assert(*pos >= 'a' && *pos <= 'h'); // expect a file letter
		state->enpass_square = *pos - 'a'; // add file to enpass square
		pos++; // consume file
		assert(*pos == '3' || *pos == '6'); // expect a 3 or 6 for rank
		state->enpass_square += (*pos - '1') * 8; // add rank * 8 to complete square_id calculation
		pos ++; // consume rank
	}
	assert(*pos == ' '); // expect a space
	pos++; // consume the space

	// parse half move clock 
	assert(*pos >= '0' && *pos <= '9');
	state->clock = stoi(pos, &idx);
	pos += idx; // increment pos to end of number
	assert(*pos == ' ');
	pos++;

	// parse fullmove counter (stored in state->halfmoves for Board)
	assert(*pos >= '0' && *pos <= '9');
	state->halfmoves = (stoi(pos, &idx) - 1) * 2 + (state->turn >> 4); // add 1 halfmove if its black's turn - fullmoves are incremented after black
	pos += idx;
	assert(*pos == '\0'); // should have reached end of fen string

	// Generate Zobstist hash and store it - this should be the only place this needs to be sone from scratch (for non-debug purposes anyways)
	state->zobrist = genZobrist();
	
}

// Initializes board to starting position
Board::Board() {
	
	// initialize stateStack vector
	stateStack.reserve(STATE_STACK_STARTING_SIZE);
	stateStack.emplace_back();
	state = stateStack.data();

	// place the pieces
	state->squares[0] = WHITE | ROOK;
	state->squares[1] = WHITE | KNIGHT;
	state->squares[2] = WHITE | BISHOP;
	state->squares[3] = WHITE | QUEEN;
	state->squares[4] = WHITE | KING;
	state->squares[5] = WHITE | BISHOP;
	state->squares[6] = WHITE | KNIGHT;
	state->squares[7] = WHITE | ROOK;
	for(uint8_t i = 8; i < 16; i++) {
		state->squares[i] = WHITE | PAWN;
	}
	for(uint8_t i = 16; i < 48; i++) {
		state->squares[i] = 0;
	}
	for(uint8_t i = 48; i < 56; i++) {
		state->squares[i] = BLACK | PAWN;
	}
	state->squares[56] = BLACK | ROOK;
	state->squares[57] = BLACK | KNIGHT;
	state->squares[58] = BLACK | BISHOP;
	state->squares[59] = BLACK | QUEEN;
	state->squares[60] = BLACK | KING;
	state->squares[61] = BLACK | BISHOP;
	state->squares[62] = BLACK | KNIGHT;
	state->squares[63] = BLACK | ROOK;

	state->king_pos[0] = 4;
	state->king_pos[1] = 60;

	state->turn = WHITE;
	for(uint8_t i = 0; i < 4; i++) {
		state->castling_avail[i] = true;
	}

	state->enpass_square = NO_ENPASS;
	state->clock = 0;
	state->halfmoves = 0;

	// initialize zobrist hash
	state->zobrist = starting_hash;
}

static void print_vector(vector<uint8_t> v) {
	printf("<");
	for(int i = 0; i < v.size(); i++) {
		printf("%s", square_name(v[i]));
		if(i != v.size() - 1) {
			printf(", ");
		}
	}
	printf(">\n");
}

static void print_vector(vector<vector<uint8_t> > v) {
	if(v.size() == 0) {
		printf("<>\n");
	} else {
		printf("<\n");
		for(int i = 0; i < v.size(); i++) {
			printf("\t");
			print_vector(v[i]);
		}
		printf(">\n");
	}
}

static void print_vector(vector<Move> v) {
	printf("[");
	for(int i = 0; i < v.size(); i++) {
		Move m = v[i];
		printf("\'%s%s", square_name(m.from_square), square_name(m.to_square));
		switch(m.promotion_type) {
			case KNIGHT: printf("k"); break;
			case BISHOP: printf("b"); break;
			case ROOK: printf("r"); break;
			case QUEEN: printf("q"); break;
		}
		printf("\'");
		if(i != v.size() - 1) {
			printf(", ");
		}
	}
	printf("]\n");
}

void Board::checksAndPins(SquareSet& check_path, bool& check, bool& double_check,
			map<uint8_t, SquareSet >& pinned_squares) {

	uint8_t king = king_pos(state->turn);

	// check for knight checks
	vector<vector<uint8_t> >* knight_attack_paths = &attack_paths(king, KNIGHT);
	for(int p = 0; p < knight_attack_paths->size(); p++) {
		uint8_t sq = (*knight_attack_paths)[p][0];
		if(state->squares[sq] == (other_color(state->turn) | KNIGHT)) { // Knight check
			check = true;
			check_path.insert(sq);
		}
	}

	// check for Bishop / Rook checks
		/* This uses a weird for loop to run the checking code for bishops/rooks/queens
			in two passes looking at bishop moves and then rook moves */

	vector<vector<uint8_t> >* bishop_attack_paths = &attack_paths(king, BISHOP);
	vector<vector<uint8_t> >* rook_attack_paths = &attack_paths(king, ROOK);
	
	// this points to the array currently being iterated
	vector<vector<uint8_t> >* paths = bishop_attack_paths;
	uint8_t checking_piece = BISHOP;

	for(uint8_t c = 0; c < 2; c++, paths = rook_attack_paths, checking_piece = ROOK) { // it was this or gotos - I aint making a method
		for(int p = 0; p < (*paths).size(); p++) {
			uint8_t blocked = 255;
			for(int s = 0; s < (*paths)[p].size(); s++) {
				uint8_t sq = (*paths)[p][s];
				if(state->squares[sq] != 0) {
					if(state->squares[sq] == (other_color(state->turn) | checking_piece) || 
							state->squares[sq] == (other_color(state->turn) | QUEEN)) { // Bishop/queen check or pin
						if(blocked < 64) { // discovered a pin
							SquareSet pinned_set;
							for(int i = 0; i <= s; i++) {
								pinned_set.insert((*paths)[p][i]);
							}
							pinned_squares.insert(pair<uint8_t, SquareSet >(blocked, pinned_set));
						} else if(!check){ // discovered first check
							check = true;
							for(int i = 0; i <= s; i++) {
								check_path.insert((*paths)[p][i]);
							}
						} else { // discovered second check
							double_check = true;
						}
						break;
					} else if(color(state->squares[sq]) == state->turn) { // potential pin
						if(blocked < 64) { // double block = no pin
							break;
						} else { // potential pin
							blocked = sq;
						}
					} else { // enemy piece not delivering check
						break;
					}
				}
			}
		}
	}

	// check for pawn checks
	vector<uint8_t>* pawn_attack_squares = &pawn_attack_squares(king, state->turn);
	for(uint8_t s = 0; s < pawn_attack_squares->size(); s++) {
		uint8_t sq = (*pawn_attack_squares)[s];
		if(state->squares[sq] == (other_color(state->turn) | PAWN)) { // discovered pawn check
			if(!check) { // first check discovered
				check = true;
				check_path.insert(sq);
			} else { // second check
				double_check = true;
			}
		}
	}

	// ------------------------ 
	// printf("---\n");
	// printf("check : %s\n", check ? "true" : "false");
	// printf("double_check : %s\n", double_check ? "true" : "false");
	// printf("pinned_squares:\n");
	// print_vector(pinned_squares);
	// printf("pinned_sets:\n");
	// print_vector(pinned_sets);
	// printf("check_path:\n");
	// print_vector(check_path);
}


/*
	fills in attack_squares with square ids that color can move to psuedolegally
	Intended for use in determining valid king moves
*/
void Board::attackSquares(SquareSet& attack_squares, uint8_t color, SquareSet& check_path_end) {
	for(uint8_t sq = 0; sq < 64; sq++) {
		if(color(state->squares[sq]) == color) {
			if(piece(state->squares[sq]) == PAWN) {
				for(int s = 0; s < pawn_attack_squares(sq, color).size(); s++) {
					attack_squares.insert(pawn_attack_squares(sq, color)[s]);
				}
			} else {
				vector<vector<uint8_t> >& paths = attack_paths(sq, piece(state->squares[sq]));
				for(int p = 0; p < paths.size(); p++) {
					vector<uint8_t>& path = paths[p];
					for(int s = 0; s < path.size(); s++) {
						if(state->squares[path[s]] == 0) { // attacking empty square
							attack_squares.insert(path[s]);
						} else { // attacking piece
							attack_squares.insert(path[s]);
							if(state->squares[path[s]] == (other_color(color) | KING) && s + 1 < path.size()) {
								check_path_end.insert(path[s+1]);
							}
							break;
						}
					}
				}
			}
		}
	}
}

vector<Move> Board::legalMoves() {

	vector<Move> moves;
	moves.reserve(40);

	SquareSet check_path; // only look at if check == True && double_check == False // lists squares which a piece may move to or capture on to stop check
	SquareSet check_path_end; // square_ids of squares covered by check bechind king - 255 if NA
	bool check = false; // true if the king is in check
	bool double_check = false; // true if the king is in check and is threatened by two pieces from different directions
	map<uint8_t, SquareSet > pinned_squares; // key = square of pinned piece, value = squares it is pinned to
	SquareSet attack_squares; // set of all squares the other color may psuedolegally move to

	// build all the check info
	checksAndPins(check_path, check, double_check, pinned_squares);
	// build attack_squares
	attackSquares(attack_squares, other_color(state->turn), check_path_end);


	// Calculate normal (non-castle) king moves first
	uint8_t king = king_pos(state->turn);
	for(int p = 0; p < attack_paths(king, KING).size(); p++) {
		uint8_t sq = attack_paths(king, KING)[p][0];
		if(color(state->squares[sq]) != state->turn && !attack_squares.contains(sq) && !check_path_end.contains(sq)) { // sq is safe
			moves.emplace_back(king, sq);
		}
	}

	// printf("king is at %s\n", square_name(king));
	// printf("finished king moves\n");
	// print_vector(moves);

	if(double_check) { // double_check -> king must move
		return moves;
	}

	// Next do castles
	if(castle_avail(state->turn, CASTLE_KING) && !check &&             // check if the king can castle kingside
				state->squares[king+1] == 0 && state->squares[king+2] == 0 &&
				!attack_squares.contains(king+1) &&
				!attack_squares.contains(king+2)) {
		moves.emplace_back(king, king+2, MOVE_CASTLE, CASTLE_KING);
	}
	if(castle_avail(state->turn, CASTLE_QUEEN) && !check &&            // check if the king can castle queenside
				state->squares[king-1] == 0 && state->squares[king-2] == 0 && state->squares[king-3] == 0 &&
				!attack_squares.contains(king-1) &&
				!attack_squares.contains(king-2)) {
		moves.emplace_back(king, king-2, MOVE_CASTLE, CASTLE_QUEEN);
	}

	// printf("finished castle moves\n");
	// print_vector(moves);

	/*
		All other moves must fulfil the following requirements
		 - if from_square is in a pinned set, to_square must be in the pinned set
		 - if check == true, move must be a king move or to_square must be in check_path
	*/
	for(int sq = 0; sq < 64; sq++) {
		if(color(state->squares[sq]) == state->turn && sq != king) { // found piece to look for moves

			bool pinned = _contains(pinned_squares, sq);
			SquareSet* pinned_set = pinned ? &pinned_squares[sq] : NULL;

			if(piece(state->squares[sq]) == PAWN) { // piece is a pawn
				// look at attacks first (captures + en-passant)
				vector<uint8_t>& attacks = pawn_attack_squares(sq, state->turn);
				for(int s = 0; s < attacks.size(); s++) { // iterate over attack squares
					uint8_t asq = attacks[s];
					uint8_t csq = enpass_capture_square(asq);
					if(asq == state->enpass_square &&
								(state->squares[csq] == (other_color(state->turn) | PAWN)) &&
								(!pinned || pinned_set->contains(asq)) &&
								(!check || check_path.contains(csq))) { // potential enpassant
						/* 
							The if statement qualifies that the movement of the capturing pawn is legal, but
							Need to check that removing the captured pawn doesnt put king in check
							This is done by looking for rook/bishops/queens in line with the king and removed pawn
							Technically, no legal position can have a revealed bishop check from enpassant, but i'll
							still check anyways since this can come up in artificial positions
							revealed rook checks can only possible arrise horizontally
						*/
						int8_t df = file(csq) - file(king),
							dr = rank(csq) - rank(king);
						uint8_t pinning_piece;
						if(dr == 0) { // look for horizontal pin
							pinning_piece = ROOK;
						} else if(df == dr || -df == dr) { // look for revealed diagonal pin
							pinning_piece = BISHOP;
						} else { // no possible pin
							moves.emplace_back(sq, asq, MOVE_ENPASS, csq);
							continue;
						}
						df = (df > 0) - (df < 0); // get signs of dr and df (+1 or -1)
						dr = (dr > 0) - (dr < 0);
						bool valid = true;
						for(uint8_t f = file(csq) + df, r = rank(csq) + dr; f >= 0 && f < 8 && r >= 0 && r < 8; f += df, r+= dr) {
							uint8_t tsq = square_id(r, f);
							if(tsq != sq) {
								uint8_t pid = state->squares[tsq];
								if(pid != 0) {
									if(pid == (other_color(state->turn) | pinning_piece) || pid == (other_color(state->turn) | QUEEN)) {
										valid = false; // there is an attacker and pin
										break;
									}
									break;
								}
							}
						}
						if(!valid) { // check to make sure the pin isnt blocked on the other side
							for(uint8_t f = file(csq) - df, r = rank(csq) - dr; f >= 0 && f < 8 && r >= 0 && r < 8; f -= df, r-= dr) {
								uint8_t tsq = square_id(r, f);
								if(tsq == king) {
									break;
								} else if(tsq != sq && state->squares[tsq] != 0) {
									valid = true;
								}
							}
						}
						if(valid) {
							moves.emplace_back(sq, asq, MOVE_ENPASS, csq);
						}
					} else if(color(state->squares[asq]) == other_color(state->turn) && 
								(!pinned || pinned_set->contains(asq)) &&
								(!check || check_path.contains(asq))) {     // pawn capture
						if(rank(asq) == 0 || rank(asq) == 7) {
							moves.emplace_back(sq, asq, MOVE_PROMOTE, KNIGHT);
							moves.emplace_back(sq, asq, MOVE_PROMOTE, BISHOP);
							moves.emplace_back(sq, asq, MOVE_PROMOTE, ROOK);
							moves.emplace_back(sq, asq, MOVE_PROMOTE, QUEEN);
						} else {
							moves.emplace_back(sq, asq);
						}
					}
				}
				// Time to look at pawn pushes
				vector<uint8_t>& path = pawn_move_path(sq, state->turn);
				for(int s = 0; s < path.size(); s++) { // iterate over push squares
					uint8_t tsq = path[s];
					if(state->squares[tsq] != 0) { // There is a piece blocking the path
						break;
					}
					if((!pinned || pinned_set->contains(tsq)) && (!check || check_path.contains(tsq))) {
						if(rank(tsq) == 0 || rank(tsq) == 7) {
							moves.emplace_back(sq, tsq, MOVE_PROMOTE, KNIGHT);
							moves.emplace_back(sq, tsq, MOVE_PROMOTE, BISHOP);
							moves.emplace_back(sq, tsq, MOVE_PROMOTE, ROOK);
							moves.emplace_back(sq, tsq, MOVE_PROMOTE, QUEEN);
						} else {
							moves.emplace_back(sq, tsq);
						}
					}
				}
			} 
			else { // piece is Knight, Bishop, Rook or Queen
				vector<vector<uint8_t> >& paths = attack_paths(sq, piece(state->squares[sq]));
				for(int p = 0; p < paths.size(); p++) { // iterate over all paths the piece can take
					vector<uint8_t>& path = paths[p];
					for(int s = 0; s < path.size(); s++) { // iterate over the squares in a single path
						uint8_t tsq = path[s];
						if(color(state->squares[tsq]) == state->turn) { // path blocked by same color piece
							break;
						}
						if((!pinned || pinned_set->contains(tsq)) && (!check || check_path.contains(tsq))) { // check for pins and check
							moves.emplace_back(sq, tsq);
						}
						if(state->squares[tsq] != 0) { // move was capture (ie. blocked by other color piece)
							break;
						}
					}
				}
			}
		}
	}

	// print_vector(moves);
	return moves;
}

// precondition: move must be a valid move - undefined behavior if not
void Board::makeMove(Move move) {

	// Copy existing board state to top of stack and update state pointer
	stateStack.push_back(*state);
	state = &stateStack.back();

	// set variables for special moves (enpassant, castling right changes, and promotion)
	uint8_t from_pid = state->squares[move.from_square];
	uint8_t to_pid = state->squares[move.to_square];
	
	uint8_t new_enpass_square = NO_ENPASS;
	uint8_t new_clock = state->clock + 1;

	if(move.move_type == MOVE_NORMAL) {
		// if king - update king position
		// if pawn - reset 50 move clock
		// if pawn double push - set enpass square + reset 50 move clock
		// if to/from corner - disable corresponding castling rights
		// if capture - reset 50 move clock

		if(piece(from_pid) == KING) { // king move
			king_pos(state->turn) = move.to_square;
			castle_avail(state->turn, CASTLE_KING) = false;
			castle_avail(state->turn, CASTLE_QUEEN) = false;
		} else if(piece(from_pid) == PAWN) { // pawn move
			if((move.from_square - move.to_square == 16) || (move.to_square - move.from_square == 16)) { // double pawn push
				new_enpass_square = (move.from_square + move.to_square) >> 1; // Average to and from square to get enpass square (1 behind to_square)
			}
			new_clock = 0;
		}

		if(to_pid != 0) { // capture
			// This excludes enpass captures, but that is okay - it is handled seperately
			new_clock = 0;
		}

		// Check for invalidations of castling abilities
		//     TODO: This can probably be skipped in most instances in exchange for more complex code
		if(move.from_square == 0 || move.to_square == 0) // white queen rook invalid
			castle_avail(WHITE, CASTLE_QUEEN) = false;
		if(move.from_square == 7 || move.to_square == 7) // white king rook invalid
			castle_avail(WHITE, CASTLE_KING) = false;
		if(move.from_square == 56 || move.to_square == 56) // black queen rook invalid
			castle_avail(BLACK, CASTLE_QUEEN) = false;
		if(move.from_square == 63 || move.to_square == 63) // black king rook invalid
			castle_avail(BLACK, CASTLE_KING) = false;

		// Move pieces
		state->squares[move.to_square] = state->squares[move.from_square];
		state->squares[move.from_square] = 0;
		
	} else if(move.move_type == MOVE_ENPASS) {
		
		// move/capture pieces
		state->squares[move.to_square] = state->squares[move.from_square];
		state->squares[move.from_square] = 0;
		state->squares[move.enpass_capture_square] = 0;
		new_clock = 0;

	} else if(move.move_type == MOVE_CASTLE) {

		// Turn off castling
		castle_avail(state->turn, CASTLE_KING) = false;
		castle_avail(state->turn, CASTLE_QUEEN) = false;

		// move king
		state->squares[move.to_square] = state->squares[move.from_square];
		state->squares[move.from_square] = 0;
		king_pos(state->turn) = move.to_square;

		// Move rook
		if(move.castle_direction == CASTLE_KING) { // kingside
			state->squares[move.to_square + 1] = 0;
			state->squares[move.to_square - 1] = state->turn | ROOK;
		} else if(move.castle_direction == CASTLE_QUEEN) { // queenside
			state->squares[move.to_square - 2] = 0;
			state->squares[move.to_square + 1] = state->turn | ROOK;
		} else {
			assert(false);
		}

	} else if(move.move_type == MOVE_PROMOTE) {
		// Check for invalidations of castling abilities
		if(move.to_square == 0)  castle_avail(WHITE, CASTLE_QUEEN) = false; // white queen rook invalid
		if(move.to_square == 7)  castle_avail(WHITE, CASTLE_KING)  = false; // white king rook invalid
		if(move.to_square == 56) castle_avail(BLACK, CASTLE_QUEEN) = false; // black queen rook invalid
		if(move.to_square == 63) castle_avail(BLACK, CASTLE_KING)  = false; // black king rook invalid
		
		// move pawn and tranform to new piece
		state->squares[move.to_square] = state->turn | move.promotion_type;
		state->squares[move.from_square] = 0;
		new_clock = 0;


	} else { // Invalid move_type
		assert(false);
	}

	// Update common values
	state->turn = other_color(state->turn);
	state->enpass_square = new_enpass_square;
	state->clock = new_clock;
	state->halfmoves++;
	
	// !!! // TODO: update zobrist

}

void Board::unmakeMove() {
	stateStack.pop_back();
	state = &stateStack.back();
}

uint64_t Board::countPositions(uint8_t depth) {
	if(depth == 0) {
		return 1;
	} else if(depth == 1) {
		vector<Move> moves = legalMoves();
		return moves.size();
	}
	uint64_t count = 0;
	vector<Move> moves = legalMoves();
	for(int i = 0; i < moves.size(); i++) {
		makeMove(moves[i]);
		count += countPositions(depth - 1);
		unmakeMove();
	}
	return count;
}

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
			if(state->squares[square_id] != 0) { // piece is present
				if(gap_size > '0') {
					fen[pos++] = gap_size;
					gap_size = '0';
				}
				switch(state->squares[square_id]) {
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
	switch(state->turn) {
		case WHITE : fen[pos++] = 'w'; break;
		case BLACK : fen[pos++] = 'b'; break;
		default : assert(false);
	}
	fen[pos++] = ' ';

	// gen castling info
	if(*((uint32_t*) state->castling_avail) == 0) { // no castling
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
	if(state->enpass_square == NO_ENPASS) { // no enpassant
		fen[pos++] = '-';		
	} else {
		fen[pos++] = 'a' + file(state->enpass_square);
		fen[pos++] = '1' + rank(state->enpass_square);
	}
	fen[pos++] = ' ';
	
	// gen halfmove clock
	len = sprintf(&fen[pos], "%d", state->clock);
	assert(len > 0);
	pos += len;
	fen[pos++] = ' ';

	// gen fullmove counter
	len = sprintf(&fen[pos], "%d", state->halfmoves / 2 + 1);
	assert(len > 0);
	pos += len;

	fen[pos] = '\0';
	return fen;
}

uint64_t Board::genZobrist() {
	
	uint64_t zob = 0;
	for(uint8_t i = 0; i < 64; i++) {
		if(state->squares[i] != 0) {
			zob ^= zobrist_piece_at(i, state->squares[i]);
		}
	}
	if(state->turn == BLACK) {
		zob ^= zobrist_blacks_move;
	}
	zob ^= (castle_avail(WHITE, CASTLE_KING))  ? zobrist_castle_avail(WHITE, CASTLE_KING)  : 0;
	zob ^= (castle_avail(WHITE, CASTLE_QUEEN)) ? zobrist_castle_avail(WHITE, CASTLE_QUEEN) : 0;
	zob ^= (castle_avail(BLACK, CASTLE_KING))  ? zobrist_castle_avail(BLACK, CASTLE_KING)  : 0;
	zob ^= (castle_avail(BLACK, CASTLE_QUEEN)) ? zobrist_castle_avail(BLACK, CASTLE_QUEEN) : 0;
	if(state->enpass_square != NO_ENPASS) {
		zob ^= zobrist_enpass_file(file(state->enpass_square));
	}
	return zob;
}