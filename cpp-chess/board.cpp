#include <stdint.h>
#include <stdio.h>
#include <vector>
#include <string>
#include <set>
#include <map>
#define contains(setmap, key) ((setmap).find(key) != (setmap).end())

#include "board.h"
#include "move.h"
#include "attack-squares.h"
#include "zobrist.h"

using namespace std;

#define TRANSITION_VECTOR_STARTING_SIZE 128

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
	char* pos = (char*) fen;
	size_t idx;

	// Parse position info
	uint8_t rank = 7;
	uint8_t* square;
	for(square = &squares[56]; square >= squares && rank >= 0; ) {
	// for(square = &squares[63]; square >= squares; ) {
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
					   king_pos(WHITE) = (uint8_t) (square - squares);
					   square++;
					   break;
			case 'k' : *square = BLACK | KING   ;
					   king_pos(BLACK) = (uint8_t) (square - squares);
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

	// initialize transition vector
	transitions.reserve(TRANSITION_VECTOR_STARTING_SIZE);

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

	// initialize transition vector
	transitions.reserve(TRANSITION_VECTOR_STARTING_SIZE);

	zobrist = starting_hash;
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

void Board::checksAndPins(set<uint8_t>& check_path, bool& check, bool& double_check,
			map<uint8_t, set<uint8_t> >& pinned_squares) {

	uint8_t king = king_pos(turn);

	// check for knight checks
	vector<vector<uint8_t> >* knight_attack_paths = &attack_paths(king, KNIGHT);
	for(int p = 0; p < knight_attack_paths->size(); p++) {
		uint8_t sq = (*knight_attack_paths)[p][0];
		if(squares[sq] == (other_color(turn) | KNIGHT)) { // Knight check
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
				if(squares[sq] != 0) {
					if(squares[sq] == (other_color(turn) | checking_piece) || 
							squares[sq] == (other_color(turn) | QUEEN)) { // Bishop/queen check or pin
						if(blocked < 64) { // discovered a pin
							set<uint8_t> pinned_set;
							for(int i = 0; i <= s; i++) {
								pinned_set.insert((*paths)[p][i]);
							}
							pinned_squares.insert(pair<uint8_t, set<uint8_t> >(blocked, pinned_set));
						} else if(!check){ // discovered first check
							check = true;
							for(int i = 0; i <= s; i++) {
								check_path.insert((*paths)[p][i]);
							}
						} else { // discovered second check
							double_check = true;
						}
						break;
					} else if(color(squares[sq]) == turn) { // potential pin
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
	vector<uint8_t>* pawn_attack_squares = &pawn_attack_squares(king, turn);
	for(uint8_t s = 0; s < pawn_attack_squares->size(); s++) {
		uint8_t sq = (*pawn_attack_squares)[s];
		if(squares[sq] == (other_color(turn) | PAWN)) { // discovered pawn check
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
void Board::attackSquares(set<uint8_t>& attack_squares, uint8_t color, set<uint8_t>& check_path_end) {
	for(uint8_t sq = 0; sq < 64; sq++) {
		if(color(squares[sq]) == color) {
			if(piece(squares[sq]) == PAWN) {
				for(int s = 0; s < pawn_attack_squares(sq, color).size(); s++) {
					attack_squares.insert(pawn_attack_squares(sq, color)[s]);
				}
			} else {
				vector<vector<uint8_t> >& paths = attack_paths(sq, piece(squares[sq]));
				for(int p = 0; p < paths.size(); p++) {
					vector<uint8_t>& path = paths[p];
					for(int s = 0; s < path.size(); s++) {
						if(squares[path[s]] == 0) { // attacking empty square
							attack_squares.insert(path[s]);
						} else { // attacking piece
							attack_squares.insert(path[s]);
							if(squares[path[s]] == (other_color(color) | KING) && s + 1 < path.size()) {
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

	set<uint8_t> check_path; // only look at if check == True && double_check == False // lists squares which a piece may move to or capture on to stop check
	set<uint8_t> check_path_end; // square_ids of squares covered by check bechind king - 255 if NA
	bool check = false; // true if the king is in check
	bool double_check = false; // true if the king is in check and is threatened by two pieces from different directions
	map<uint8_t, set<uint8_t> > pinned_squares; // key = square of pinned piece, value = squares it is pinned to
	set<uint8_t> attack_squares; // set of all squares the other color may psuedolegally move to

	// build all the check info
	checksAndPins(check_path, check, double_check, pinned_squares);
	// build attack_squares
	attackSquares(attack_squares, other_color(turn), check_path_end);


	// Calculate king moves first
	uint8_t king = king_pos(turn);
	for(int p = 0; p < attack_paths(king, KING).size(); p++) {
		uint8_t sq = attack_paths(king, KING)[p][0];
		if(color(squares[sq]) != turn && !contains(attack_squares, sq) && !contains(check_path_end, sq)) { // sq is safe
			moves.push_back(Move(king, sq));
		}
	}

	// printf("king is at %s\n", square_name(king));
	// printf("finished king moves\n");
	// print_vector(moves);

	if(double_check) { // double_check -> king must move
		return moves;
	}

	// Next do castles
	if(castle_avail(turn, CASTLE_KING) && !check &&             // check if the king can castle kingside
				squares[king+1] == 0 && squares[king+2] == 0 &&
				!contains(attack_squares, king+1) &&
				!contains(attack_squares, king+2)) {
		moves.push_back(Move(king, king+2));
	}
	if(castle_avail(turn, CASTLE_QUEEN) && !check &&            // check if the king can castle queenside
				squares[king-1] == 0 && squares[king-2] == 0 && squares[king-3] == 0 &&
				!contains(attack_squares, king-1) &&
				!contains(attack_squares, king-2)) {
		moves.push_back(Move(king, king-2));
	}

	// printf("finished castle moves\n");
	// print_vector(moves);

	/*
		All other moves must fulfil the following requirements
		 - if from_square is in a pinned set, to_square must be in the pinned set
		 - if check == true, move must be a king move or to_square must be in check_path
	*/
	for(int sq = 0; sq < 64; sq++) {
		if(color(squares[sq]) == turn && sq != king) { // found piece to look for moves

			bool pinned = contains(pinned_squares, sq);
			set<uint8_t>* pinned_set = pinned ? &pinned_squares[sq] : NULL;

			if(piece(squares[sq]) == PAWN) { // piece is a pawn
				// look at attacks first (captures + en-passant)
				vector<uint8_t>& attacks = pawn_attack_squares(sq, turn);
				for(int s = 0; s < attacks.size(); s++) { // iterate over attack squares
					uint8_t asq = attacks[s];

					if(asq == enpass_square &&
								(!pinned || contains(*pinned_set, asq)) &&
								(!check || contains(check_path, enpass_capture_square(asq)))) { // potential enpassant
						/* 
							The if statement qualifies that the movement of the capturing pawn is legal, but
							Need to check that removing the captured pawn doesnt put king in check
							This is done by looking for rook/bishops/queens in line with the king and removed pawn
							Technically, no legal position can have a revealed bishop check from enpassant, but i'll
							still check anyways since this can come up in artificial positions
							revealed rook checks can only possible arrise horizontally
						*/
						uint8_t csq = enpass_capture_square(asq);
						int8_t df = file(csq) - file(king),
							dr = rank(csq) - rank(king);
						uint8_t pinning_piece;
						if(dr == 0) { // look for horizontal pin
							pinning_piece = ROOK;
						} else if(df == dr || -df == dr) { // look for revealed diagonal pin
							pinning_piece = BISHOP;
						} else { // no possible pin
							moves.push_back(Move(sq, asq));
							continue;
						}
						df = (df > 0) - (df < 0); // get signs of dr and df (+1 or -1)
						dr = (dr > 0) - (dr < 0);
						bool valid = true;
						for(uint8_t f = file(csq) + df, r = rank(csq) + dr; f >= 0 && f < 8 && r >= 0 && r < 8; f += df, r+= dr) {
							uint8_t tsq = square_id(r, f);
							if(tsq != sq) {
								uint8_t pid = squares[tsq];
								if(pid != 0) {
									if(pid == (other_color(turn) | pinning_piece) || pid == (other_color(turn) | QUEEN)) {
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
								} else if(squares[tsq] != 0) {
									valid = true;
								}
							}
						}
						if(valid) {
							moves.push_back(Move(sq, asq));
						}
					} else if(color(squares[asq]) == other_color(turn) && 
								(!pinned || contains(*pinned_set, asq)) &&
								(!check || contains(check_path, asq))) {     // pawn capture
						if(rank(asq) == 0 || rank(asq) == 7) {
							moves.push_back(Move(sq, asq, KNIGHT));
							moves.push_back(Move(sq, asq, BISHOP));
							moves.push_back(Move(sq, asq, ROOK));
							moves.push_back(Move(sq, asq, QUEEN));
						} else {
							moves.push_back(Move(sq, asq));
						}
					}
				}
				// Time to look at pawn pushes
				vector<uint8_t>& path = pawn_move_path(sq, turn);
				for(int s = 0; s < path.size(); s++) { // iterate over push squares
					uint8_t tsq = path[s];
					if(squares[tsq] != 0) { // There is a piece blocking the path
						break;
					}
					if((!pinned || contains(*pinned_set, tsq)) && (!check || contains(check_path, tsq))) {
						if(rank(tsq) == 0 || rank(tsq) == 7) {
							moves.push_back(Move(sq, tsq, KNIGHT));
							moves.push_back(Move(sq, tsq, BISHOP));
							moves.push_back(Move(sq, tsq, ROOK));
							moves.push_back(Move(sq, tsq, QUEEN));
						} else {
							moves.push_back(Move(sq, tsq));
						}
					}
				}
			} 
			else { // piece is Knight, Bishop, Rook or Queen
				vector<vector<uint8_t> >& paths = attack_paths(sq, piece(squares[sq]));
				for(int p = 0; p < paths.size(); p++) { // iterate over all paths the piece can take
					vector<uint8_t>& path = paths[p];
					for(int s = 0; s < path.size(); s++) { // iterate over the squares in a single path
						uint8_t tsq = path[s];
						if(color(squares[tsq]) == turn) { // path blocked by same color piece
							break;
						}
						if((!pinned || contains(*pinned_set, tsq)) && (!check || contains(check_path, tsq))) { // check for pins and check
							moves.push_back(Move(sq, tsq));
						}
						if(squares[tsq] != 0) { // move was capture (ie. blocked by other color piece)
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
	Transition* trans = new Transition(move, this);

	// set variables for special moves (enpassant, castling right changes, and promotion)
	uint8_t from_pid = squares[move.from_square];
	uint8_t to_pid = squares[move.to_square];
	
	uint8_t new_enpass_square = NO_ENPASS;
	uint8_t new_to_square_pid = new_to_square_pid = squares[move.from_square];
	uint8_t new_clock = clock + 1;


	if(trans->is_special == TRANSITION_ENPASS) { // enpassant
		new_clock = 0;
		squares[trans->special_info.capture_square_id] = 0;
		goto endUpdate;
	} else if(trans->is_special == TRANSITION_PROMOTE) { // promotion
		new_clock = 0;
		new_to_square_pid = turn | piece(move.promotion_type);
	} else if(trans->is_special == TRANSITION_CASTLE) { // castle
		castle_avail(turn, CASTLE_KING) = false;
		castle_avail(turn, CASTLE_QUEEN) = false;
		switch(turn | trans->special_info.castle_type) {
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
		king_pos(turn) = move.to_square;
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
		king_pos(turn) = move.to_square;
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
	if(trans->capture_p_id != 0) {
		new_clock = 0;
	}
	clock = new_clock;
	halfmoves++;
	
	// change turn
	turn = other_color(turn);

	// add transition to transition vector
	transitions.push_back(trans);

	// !!!
	// Update zobrist hash
}

Move Board::unmakeMove() {
	assert(!transitions.empty());

	// get transition info
	Transition* trans = transitions.back();

	// restore board metadata
	turn = other_color(turn);
	*((uint32_t*)&castling_avail) = *((uint32_t*)&trans->castling_avail);
	enpass_square = trans->enpass_square;
	clock = trans->clock;
	halfmoves -= 1;
	zobrist = trans->zobrist;

	// restore piece positions
	if(trans->is_special == TRANSITION_PROMOTE) { // promotion
		squares[trans->move.from_square] = turn | PAWN;
		if(trans->capture_p_id != 0) { // replace captured piece if there was one
			squares[trans->special_info.capture_square_id] = trans->capture_p_id;
		} else { // remove promoted piece
			squares[trans->move.to_square] = 0;
		}
	} else if(trans->is_special == TRANSITION_CASTLE) { // castle
		switch(turn | trans->special_info.castle_type) { // move the rook back
			case WHITE | CASTLE_QUEEN :
				squares[0] = squares[3];
				squares[3] = 0;
				break;
			case WHITE | CASTLE_KING :
				squares[7] = squares[5];
				squares[5] = 0;
				break;
			case BLACK | CASTLE_QUEEN :
				squares[56] = squares[59];
				squares[59] = 0;
				break;
			case BLACK | CASTLE_KING :
				squares[63] = squares[61];
				squares[61] = 0;
				break;
			default : assert(false);
		}
		squares[trans->move.from_square] = squares[trans->move.to_square];
		squares[trans->move.to_square] = 0;
		king_pos(turn) = trans->move.from_square;
	} else { // Not a castle or promotion
		squares[trans->move.from_square] = squares[trans->move.to_square];
		squares[trans->move.to_square] = 0;
		if(trans->capture_p_id != 0) { // replace captured piece if there was one
			squares[trans->special_info.capture_square_id] = trans->capture_p_id;
		}
		if(piece(squares[trans->move.from_square]) == KING) {
			king_pos(turn) = trans->move.from_square;
		}
	}

	// clean up and return
	Move move = trans->move;
	delete trans;
	transitions.pop_back();
	return move;
}

uint64_t Board::countPositions(uint8_t depth) {
	uint64_t count = 0;
	vector<Move> moves = legalMoves();
	if(depth == 1) {
		return moves.size();
	}
	for(int i = 0; i < moves.size(); i++) {
		makeMove(moves[i]);
		count += countPositions(depth - 1);
		unmakeMove();
	}
	return count;
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