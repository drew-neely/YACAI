#include <stdint.h>
#include <stdio.h>
#include <vector>

#include "board.h"
#include "attack-squares.h"

using namespace std;

_AttackSquares AttackSquares;

static vector<uint8_t> travel_in_dir(uint8_t start, int8_t dr, int8_t df, int8_t max_dist) {
	int8_t rank = rank(start);
	int8_t file = file(start);
	vector<uint8_t> path;
	rank += dr;
	file += df;
	while(rank >= 0 && rank < 8 && file >= 0 && file < 8 && max_dist != 0) {
		path.push_back(square_id(rank, file));
		rank += dr;
		file += df;
		max_dist--;
	}
	return path;
}

static vector<uint8_t> travel_in_dir(uint8_t start, int8_t dr, int8_t df) {
	return travel_in_dir(start, dr, df, -1);
}

const uint8_t knight_dirs = 8;
const int8_t knight_dr[] = {-2, -2, -1, -1,  1, 1, 2,  2};
const int8_t knight_df[] = { 1, -1, -2,  2, -2, 2, 1, -1};

const uint8_t bishop_dirs = 4;
const int8_t bishop_dr[] = {1,  1, -1, -1};
const int8_t bishop_df[] = {1, -1,  1, -1};

const uint8_t rook_dirs = 4;
const int8_t rook_dr[] = {0,  0, 1, -1};
const int8_t rook_df[] = {1, -1, 0,  0};

const uint8_t queen_dirs = 8;
const int8_t queen_dr[] = {0,  0, 1, -1, 1,  1, -1, -1};
const int8_t queen_df[] = {1, -1, 0,  0, 1, -1,  1, -1};
// The King direction data is the same as queen just with max_dist = 1

const uint8_t pawn_attack_dirs = 2;
const int8_t white_pawn_attack_dr[] = { 1, 1};
const int8_t white_pawn_attack_df[] = {-1, 1};
const int8_t black_pawn_attack_dr[] = {-1, -1};
const int8_t black_pawn_attack_df[] = {-1,  1};

#define WHITE_INDEX 0
#define BLACK_INDEX 1

_AttackSquares::_AttackSquares() : 
			_attack_squares(64), _pawn_attack_squares(64), _pawn_move_squares(64) {

	vector<uint8_t> path;

	for(int sq = 0; sq < 64; sq++) {
		// init attack_squares at index
		_attack_squares[sq] = vector<vector<vector<uint8_t> > >(6);

		// _attack_squares[sq][PAWN = 0] is left empty
		// pawns are dealt with seperately, I would just
		// prefer to have an empty slot in the vector than
		// deal with index calculation (ie. piece - 1)

		// knight moves
		for(int i = 0; i < knight_dirs; i++) {
			path = travel_in_dir(sq, knight_dr[i], knight_df[i], 1);
			if(!path.empty()) {
				_attack_squares[sq][KNIGHT].push_back(path);
			}
		}
		
		// bishop moves
		for(int i = 0; i < bishop_dirs; i++) {
			path = travel_in_dir(sq, bishop_dr[i], bishop_df[i]);
			if(!path.empty()) {
				_attack_squares[sq][BISHOP].push_back(path);
			}
		}

		// rook moves
		for(int i = 0; i < rook_dirs; i++) {
			path = travel_in_dir(sq, rook_dr[i], rook_df[i]);
			if(!path.empty()) {
				_attack_squares[sq][ROOK].push_back(path);
			}
		}

		// queen moves
		for(int i = 0; i < queen_dirs; i++) {
			path = travel_in_dir(sq, queen_dr[i], queen_df[i]);
			if(!path.empty()) {
				_attack_squares[sq][QUEEN].push_back(path);
			}
		}

		// king moves (uses queen directions with max dist 1)
		for(int i = 0; i < queen_dirs; i++) {
			path = travel_in_dir(sq, queen_dr[i], queen_df[i], 1);
			if(!path.empty()) {
				_attack_squares[sq][KING].push_back(path);
			}
		}

		// initialize pawn_attack_squares at index
		_pawn_attack_squares[sq] = vector<vector<uint8_t> >(2);
		
		// white_pawn attacks
		for(int i = 0; i < pawn_attack_dirs; i++) {
			path = travel_in_dir(sq, white_pawn_attack_dr[i], white_pawn_attack_dr[i], 1);
			if(!path.empty()) {
				_pawn_attack_squares[sq][WHITE_INDEX].push_back(path[0]);
			}
		}

		// black_pawn attacks
		for(int i = 0; i < pawn_attack_dirs; i++) {
			path = travel_in_dir(sq, black_pawn_attack_dr[i], black_pawn_attack_dr[i], 1);
			if(!path.empty()) {
				_pawn_attack_squares[sq][BLACK_INDEX].push_back(path[0]);
			}
		}

		// intitalize pawn_move_squares at index
		_pawn_move_squares[sq] = vector<vector<uint8_t> >(2);

		_pawn_move_squares[sq][WHITE_INDEX] = travel_in_dir(sq,  1, 0, rank(sq) == 1 ? 2 : 1);
		_pawn_move_squares[sq][BLACK_INDEX] = travel_in_dir(sq, -1, 0, rank(sq) == 6 ? 2 : 1);

	}
}