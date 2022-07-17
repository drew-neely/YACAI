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
#include "chess_containers.h"

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

//////////////////////////////////////////////////
///////////// Board state Methods
//////////////////////////////////////////////////

/*
	test if current and other qualify as repeated positions as per the 3 move repitition rule
	From Fide rule 9.2b
		"""
		Positions as in (a) and (b) are considered the same, if the same player has the move,
		pieces of the same kind and color occupy the same squares, and the possible moves of all
		the pieces of both players are the same. Positions are not the same if a pawn that could
		have been captured en passant can no longer in this manner be captured or if the right
		to castle has been changed temporarily or permanently.
		"""
	enpass_avail(enpass_info) must be used to determine the equality of enpass states.
	A BoardState with different enpass_sqaure(enpass_info) is only different with regards to the
	3 move repetition rule iff an enpassant is actually possible. If an enpass is actually possible
	this makes such that the set of available moves is different.
*/
bool BoardState::operator==(const BoardState& other) const {
	if(!(this->turn == other.turn && *(uint32_t*)this->castling_avail == *(uint32_t*)other.castling_avail )) {
		return false;
	}
	if(this->enpass_info != other.enpass_info) {
		if(enpass_avail(this->enpass_info) != enpass_avail(other.enpass_info))
			return false;
		if(enpass_avail(this->enpass_info) && enpass_square(this->enpass_info) != enpass_square(other.enpass_info))
			return false;
	}
	for(uint8_t idx = 0; idx < 64; idx++) // TODO: determine if this loop can be spead up by vectorizing with 32 or 64 bit ints
		if(this->squares[idx] != other.squares[idx]) 
			return false;
	return true;
}

//////////////////////////////////////////////////

//////////////////////////////////////////////////
///////////// Board Methods
//////////////////////////////////////////////////

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
		state->enpass_info = NO_ENPASS;
		pos ++; // consume '-'
	} else {
		uint8_t enpass_square = 0;
		assert(*pos >= 'a' && *pos <= 'h'); // expect a file letter
		enpass_square = *pos - 'a'; // add file to enpass square
		pos++; // consume file
		assert(*pos == '3' || *pos == '6'); // expect a 3 or 6 for rank
		enpass_square += (*pos - '1') * 8; // add rank * 8 to complete square_id calculation
		pos ++; // consume rank
		// determine if enpass is actually possible and set possible bit
		uint64_t enpass_capture_color = rank(enpass_square) == 2 ? WHITE : BLACK; // color of the pawn possibly threatened to be captured by enpassant
		assert(state->turn == other_color(enpass_capture_color)); // The piece being threatend by enpassant should always be the color whose turn it is not
		vector<uint8_t> capture_squares = pawn_attack_squares(enpass_square, enpass_capture_color); // get possible squares pawns can capture from
		for(uint8_t sq : capture_squares) {
			if(state->squares[sq] == (other_color(enpass_capture_color) | PAWN) ) { // there is an enpass move available
				enpass_square |= ENPASS_AVAIL_MASK;
				break;
			}
		}
		state->enpass_info = enpass_square;
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

	// Generate the initial composition
	state->composition = Composition(*state);

	// Generate initial game end reason
	// TODO : Need to check for 50 move rule, checkmate, and stalemate here
	if(state->composition.isInsufficientMaterial()) {
		state->game_end_reason = INSUFICIENT_MATERIAL;
	} else {
		state->game_end_reason = NO_GAME_END;
	}
	
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

	state->enpass_info = NO_ENPASS;
	state->clock = 0;
	state->halfmoves = 0;

	// initialize zobrist hash
	state->zobrist = starting_hash;

	// initialize the composition
	state->composition = Composition();

	// initialize game end reason
	state->game_end_reason = NO_GAME_END;

}

// Initializes board from state
Board::Board(BoardState s) {
	
	stateStack.reserve(STATE_STACK_STARTING_SIZE);
	stateStack.push_back(s);
	state = stateStack.data();

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

MoveGenerator Board::legalMoves() {
	
	// Check for insufficient material, three move repetition, and 50 move rule
	if(isDrawRepitition()) {
		state->game_end_reason = REPITION;
		co_return;
	} else if(isDrawInsuficientMaterial()) {
		state->game_end_reason = INSUFICIENT_MATERIAL;
		co_return;
	} else if(isDrawFiftyMove()) {
		state->game_end_reason = FIFTY_MOVE;
		co_return;
	}

	SquareSet check_path; // only look at if check == True && double_check == False // lists squares which a piece may move to or capture on to stop check
	SquareSet check_path_end; // square_ids of squares covered by check bechind king - 255 if NA
	bool check = false; // true if the king is in check
	bool double_check = false; // true if the king is in check and is threatened by two pieces from different directions
	map<uint8_t, SquareSet > pinned_squares; // key = square of pinned piece, value = squares it is pinned to
	SquareSet attack_squares; // set of all squares the other color may psuedolegally move to
	bool move_found = false;

	// build all the check info
	checksAndPins(check_path, check, double_check, pinned_squares);
	// build attack_squares
	attackSquares(attack_squares, other_color(state->turn), check_path_end);

	// Calculate normal (non-castle) king moves first
	uint8_t king = king_pos(state->turn);
	for(int p = 0; p < attack_paths(king, KING).size(); p++) {
		uint8_t sq = attack_paths(king, KING)[p][0];
		if(color(state->squares[sq]) != state->turn && !attack_squares.contains(sq) && !check_path_end.contains(sq)) { // sq is safe
			co_yield Move(king, sq);
			move_found = true;
		}
	}

	// printf("king is at %s\n", square_name(king));
	// printf("finished king moves\n");
	// print_vector(moves);

	if(double_check) { // double_check -> king must move
		if(!move_found) { // no moves + double check = checkmate
			state->game_end_reason = other_color(state->turn) | CHECKMATE;
		}
		co_return;
	}

	// Next do castles
	if(castle_avail(state->turn, CASTLE_KING) && !check &&             // check if the king can castle kingside
				state->squares[king+1] == 0 && state->squares[king+2] == 0 &&
				!attack_squares.contains(king+1) &&
				!attack_squares.contains(king+2)) {
		co_yield Move(king, king+2, MOVE_CASTLE, CASTLE_KING);
		move_found = true;
	}
	if(castle_avail(state->turn, CASTLE_QUEEN) && !check &&            // check if the king can castle queenside
				state->squares[king-1] == 0 && state->squares[king-2] == 0 && state->squares[king-3] == 0 &&
				!attack_squares.contains(king-1) &&
				!attack_squares.contains(king-2)) {
		co_yield Move(king, king-2, MOVE_CASTLE, CASTLE_QUEEN);
		move_found = true;
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
					if(state->enpass_info != NO_ENPASS &&
								(asq == enpass_square(state->enpass_info)) &&
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
							co_yield Move(sq, asq, MOVE_ENPASS, csq);
							move_found = true;
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
							co_yield Move(sq, asq, MOVE_ENPASS, csq);
							move_found = true;
						}
					} else if(color(state->squares[asq]) == other_color(state->turn) && 
								(!pinned || pinned_set->contains(asq)) &&
								(!check || check_path.contains(asq))) {     // pawn capture
						if(rank(asq) == 0 || rank(asq) == 7) {
							co_yield Move(sq, asq, MOVE_PROMOTE, KNIGHT);
							co_yield Move(sq, asq, MOVE_PROMOTE, BISHOP);
							co_yield Move(sq, asq, MOVE_PROMOTE, ROOK);
							co_yield Move(sq, asq, MOVE_PROMOTE, QUEEN);
						} else {
							co_yield Move(sq, asq);
						}
						move_found = true;
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
							co_yield Move(sq, tsq, MOVE_PROMOTE, KNIGHT);
							co_yield Move(sq, tsq, MOVE_PROMOTE, BISHOP);
							co_yield Move(sq, tsq, MOVE_PROMOTE, ROOK);
							co_yield Move(sq, tsq, MOVE_PROMOTE, QUEEN);
						} else {
							co_yield Move(sq, tsq);
						}
						move_found = true;
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
							co_yield Move(sq, tsq);
							move_found = true;
						}
						if(state->squares[tsq] != 0) { // move was capture (ie. blocked by other color piece)
							break;
						}
					}
				}
			}
		}
	}

	/*
		Check for game end scenarios
		(Draw by repitition, 50 move rule and insufficient material were already checked)
		Here I check for checkmate and stalemate
	*/
	if(!move_found) { // no moves = game over
		if(check) {
			state->game_end_reason = other_color(state->turn) | CHECKMATE;
		} else {
			state->game_end_reason = STALEMATE;
		}
	}

	// print_vector(moves);
	co_return;
}


/*
	legal_moves will do all the same work as this function in addition to returning the legal moves.
	This function is meant for the instances where it needs to be known if the game has ended, but 
	the possible moves do not matter if the game has not ended.

	Calling both legal_moves and setGameEndReason is inneficient
*/
void Board::setGameEndReason() {

	// execute legalMoves until a move is found, or until completion
	// legal moves will set endreason if needed, otherwise will quit
	// upon discovering a move since if there is a move available the
	// game is not over
	legalMoves().is_empty();

}

bool Board::isDrawRepitition() {

	uint64_t top_zobrist = stateStack[stateStack.size() - 1].zobrist;
	int zobrist_repeat_num = 0;
	int zobrist_repeat_idxs[2] = {-1, -1};

	int prev_clock = state->clock;
	int idx = stateStack.size() - 3;

	for(; idx >= 0; idx -= 2) { // go backwards on positions with the same player to move
		if(stateStack[idx].clock != prev_clock - 2) {
			// encountered irreversable move
			return false;
		}
		if(top_zobrist == stateStack[idx].zobrist) {
			// found a potentially repeated position
			zobrist_repeat_idxs[zobrist_repeat_num] = idx;
			zobrist_repeat_num++;
			if(zobrist_repeat_num >= 2) {
				break;
			}
		}
		prev_clock -= 2;
	}
	if(zobrist_repeat_num < 2) {
		// There's no chance for repeated positions
		return false;
	}
	// check if positions with same zobrist hash are actually the same and not just a hash conflict
	if(*state == stateStack[zobrist_repeat_idxs[0]] && *state == stateStack[zobrist_repeat_idxs[1]]) {
		// Found three repeated positions in stateStack
		return true;
	} else {
		// The repeated zobrist hashes in stateStack are due to a hash conflict rather than actual repeated positions
		// This should be a very rare case, so slow code is okay here - just needs to be correct
		printf("WARNING: Found zobrist hash conflict predicting false positive for 3 move repetition draw\n"); // print so if this shows up it can be made into a test case
		int repeat_num = 0;
		prev_clock = state->clock;

		for(idx = stateStack.size() - 3; idx >= 0; idx -= 2) { // go backwards on positions with the same player to move
			if(stateStack[idx].clock != prev_clock - 2) {
				// encountered irreversable move
				return false;
			}
			if(*state == stateStack[idx]) {
				// found a repeated position
				repeat_num++;
				if(repeat_num >= 2) {
					return true;
				}
			}
			prev_clock -= 2;
		}
		return false;
	}

}

// if the state is a checkmate state, the checkmate takes precedence over the fifty move rule - should be handled elsewhere
bool Board::isDrawFiftyMove() {
	return state->clock >= 100;
}

bool Board::isDrawInsuficientMaterial() {
	return state->composition.isInsufficientMaterial();
}

// precondition: move must be a valid move - undefined behavior if not
void Board::makeMove(Move move) {

	// Copy existing board state to top of stack and update state pointer
	stateStack.push_back(*state);
	state = &stateStack.back();

	// set variables for special moves (enpassant, castling right changes, and promotion)
	uint8_t from_pid = state->squares[move.from_square];
	uint8_t to_pid = state->squares[move.to_square];
	
	uint8_t new_enpass_info = NO_ENPASS;
	uint8_t new_clock = state->clock + 1;

	// If move was passed in externally or built from uci, do the extra work of determining the type of move
	// TODO : This is can possibly be removed by doing this check before passing into makeMove, but for probably extremely little performance benefit
	if(move.move_type == MOVE_NO_CONTEXT) {
		move.build_context(*this);
	}

	if(move.move_type == MOVE_NORMAL) {
		// if king - update king position
		// if pawn - reset 50 move clock
		// if pawn double push - set enpass square + reset 50 move clock
		// if to/from corner - disable corresponding castling rights
		// if capture - reset 50 move clock

		if(piece(from_pid) == KING) { // king move
			king_pos(state->turn) = move.to_square;
			disable_castle(state->turn, CASTLE_KING);
			disable_castle(state->turn, CASTLE_QUEEN);
		} else if(piece(from_pid) == PAWN) { // pawn move
			if((move.from_square - move.to_square == 16) || (move.to_square - move.from_square == 16)) { // double pawn push
				new_enpass_info = (move.from_square + move.to_square) >> 1; // Average to and from square to get enpass square (1 behind to_square)
				if(file(move.to_square) > 0 && state->squares[move.to_square - 1] == (other_color(state->turn) | PAWN)) { // pawn is not on left edge of board and there is an other color pawn on its left
					new_enpass_info |= ENPASS_AVAIL_MASK;
				} else if (file(move.to_square) < 7 && state->squares[move.to_square + 1] == (other_color(state->turn) | PAWN)) { // pawn is not on right edge of board and there is an other color pawn on its right
					new_enpass_info |= ENPASS_AVAIL_MASK;
				}
			}
			new_clock = 0;
		}

		if(to_pid != 0) { // capture
			// This excludes enpass captures, but that is okay - it is handled seperately
			new_clock = 0;
			state->composition.remove(to_pid, square_color(move.to_square)); // Remove piece from composition set
		}

		// Check for invalidations of castling abilities
		//     TODO: This can probably be skipped in most instances in exchange for more complex code
		if(move.from_square == 0 || move.to_square == 0)   disable_castle(WHITE, CASTLE_QUEEN); // white queen rook invalid
		if(move.from_square == 7 || move.to_square == 7)   disable_castle(WHITE, CASTLE_KING);  // white king rook invalid
		if(move.from_square == 56 || move.to_square == 56) disable_castle(BLACK, CASTLE_QUEEN); // black queen rook invalid
		if(move.from_square == 63 || move.to_square == 63) disable_castle(BLACK, CASTLE_KING);  // black king rook invalid
			
		// Move pieces
		move_piece_check_capture(move);
		
	} else if(move.move_type == MOVE_ENPASS) {
		
		// move/capture pieces
		move_piece_no_capture(move);
		state->zobrist ^= zobrist_piece_at(move.enpass_capture_square, state->squares[move.enpass_capture_square]);
		state->composition.remove(state->squares[move.enpass_capture_square], NULL_SQUARE);
		state->squares[move.enpass_capture_square] = 0;

		new_clock = 0;

	} else if(move.move_type == MOVE_CASTLE) {

		// Turn off castling
		disable_castle(state->turn, CASTLE_KING);
		disable_castle(state->turn, CASTLE_QUEEN);

		// move king
		move_piece_no_capture(move);
		king_pos(state->turn) = move.to_square;

		// Move rook
		uint8_t rook_pid = state->turn | ROOK;
		if(move.castle_direction == CASTLE_KING) { // kingside
			state->squares[move.to_square + 1] = 0;
			state->squares[move.to_square - 1] = rook_pid;
			state->zobrist ^= zobrist_piece_at(move.to_square + 1, rook_pid) ^ zobrist_piece_at(move.to_square - 1, rook_pid);
		} else if(move.castle_direction == CASTLE_QUEEN) { // queenside
			state->squares[move.to_square - 2] = 0;
			state->squares[move.to_square + 1] = rook_pid;
			state->zobrist ^= zobrist_piece_at(move.to_square - 2, rook_pid) ^ zobrist_piece_at(move.to_square + 1, rook_pid);
		} else {
			assert(false);
		}

	} else if(move.move_type == MOVE_PROMOTE) {
		// Check for invalidations of castling abilities
		if(move.to_square == 0)  disable_castle(WHITE, CASTLE_QUEEN); // white queen rook invalid
		if(move.to_square == 7)  disable_castle(WHITE, CASTLE_KING);  // white king rook invalid
		if(move.to_square == 56) disable_castle(BLACK, CASTLE_QUEEN); // black queen rook invalid
		if(move.to_square == 63) disable_castle(BLACK, CASTLE_KING);  // black king rook invalid
		
		// move pawn and tranform to new piece
		uint8_t new_pid = state->turn | move.promotion_type;
		if(state->squares[move.to_square] != 0) { // update zobrist and composition if promotion is a capture
			state->zobrist ^= zobrist_piece_at(move.to_square, state->squares[move.to_square]);
			state->composition.remove(to_pid, square_color(move.to_square));
		}
		state->zobrist ^= zobrist_piece_at(move.from_square, state->squares[move.from_square])
					   ^  zobrist_piece_at(move.to_square, new_pid);
		state->composition.remove(from_pid, NULL_SQUARE); // Remove pawn from composition
		state->composition.add(new_pid, square_color(move.to_square)); // Add promoted piece to composition
		state->squares[move.to_square] = new_pid;
		state->squares[move.from_square] = 0;

		// reset clock
		new_clock = 0;


	} else { // Invalid move_type
		assert(false);
	}

	// Update common values
	state->turn = other_color(state->turn);
	state->zobrist ^= zobrist_blacks_move;
	if(state->enpass_info != NO_ENPASS && enpass_avail(state->enpass_info)) {
		state->zobrist ^= zobrist_enpass_file(file(enpass_square(state->enpass_info)));
	}
	if(new_enpass_info != NO_ENPASS && enpass_avail(new_enpass_info)) {
		state->zobrist ^= zobrist_enpass_file(file(enpass_square(new_enpass_info)));
	}
	state->enpass_info = new_enpass_info;
	state->clock = new_clock;
	state->halfmoves++;

}

void Board::unmakeMove() {
	stateStack.pop_back();
	state = &stateStack.back();
}


string Board::get_fen() {
	string fen = ""; // longest fen string possible should be 92 bytes

	// gen position info
	for(int8_t rank = 7; rank >= 0; rank--) {
		char gap_size = '0';
		for(int8_t file = 0; file < 8; file++) {
			uint8_t square_id = rank*8+file;
			char piece_char;
			if(state->squares[square_id] != 0) { // piece is present
				if(gap_size > '0') {
					fen += gap_size;
					gap_size = '0';
				}
				switch(state->squares[square_id]) {
					case WHITE | PAWN   : fen += 'P'; break;
					case WHITE | KNIGHT : fen += 'N'; break;
					case WHITE | BISHOP : fen += 'B'; break;
					case WHITE | ROOK   : fen += 'R'; break;
					case WHITE | QUEEN  : fen += 'Q'; break;
					case WHITE | KING   : fen += 'K'; break;
					case BLACK | PAWN   : fen += 'p'; break;
					case BLACK | KNIGHT : fen += 'n'; break;
					case BLACK | BISHOP : fen += 'b'; break;
					case BLACK | ROOK   : fen += 'r'; break;
					case BLACK | QUEEN  : fen += 'q'; break;
					case BLACK | KING   : fen += 'k'; break;
					default : assert(false);
				}
			} else { // no piece here
				gap_size++;
			}
		}
		if(gap_size > '0') {
			fen += gap_size;
		}
		if(rank != 0) { 
			fen += '/';
		}
	}
	fen += ' ';
	
	// gen turn
	switch(state->turn) {
		case WHITE : fen += 'w'; break;
		case BLACK : fen += 'b'; break;
		default : assert(false);
	}
	fen += ' ';

	// gen castling info
	if(*((uint32_t*) state->castling_avail) == 0) { // no castling
		fen += '-';
	} else { // some castling
		if(castle_avail(WHITE, CASTLE_KING)) {
			fen += 'K';
		}
		if(castle_avail(WHITE, CASTLE_QUEEN)) {
			fen += 'Q';
		}
		if(castle_avail(BLACK, CASTLE_KING)) {
			fen += 'k';
		}
		if(castle_avail(BLACK, CASTLE_QUEEN)) {
			fen += 'q';
		}
	}
	fen += ' ';

	// gen enpassant square
	if(state->enpass_info == NO_ENPASS) { // no enpassant
		fen += '-';		
	} else {
		fen += square_names[enpass_square(state->enpass_info)];
	}
	fen += ' ';
	
	// gen halfmove clock
	fen += to_string(state->clock);
	fen += ' ';

	// gen fullmove counter
	fen += to_string(state->halfmoves / 2 + 1);

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
	if(state->enpass_info != NO_ENPASS && enpass_avail(state->enpass_info)) {
		zob ^= zobrist_enpass_file(file(enpass_square(state->enpass_info)));
	}
	return zob;
}