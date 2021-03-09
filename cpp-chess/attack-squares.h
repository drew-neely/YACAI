#pragma once

#include <stdint.h>
#include <stdio.h>
#include <vector>

struct _AttackSquares;
extern _AttackSquares AttackSquares;
#include "board.h"

using namespace std;

#define attack_paths(square_id, piece) (AttackSquares._attack_squares[square_id][piece])
#define pawn_attack_squares(square_id, color) (AttackSquares._pawn_attack_squares[square_id][((color) >> 3) - 1])
#define pawn_move_path(square_id, color) (AttackSquares._pawn_move_squares[square_id][((color) >> 3) - 1])

struct _AttackSquares {
	
	vector<vector<vector<vector<uint8_t> > > > _attack_squares;
	vector<vector<vector<uint8_t> > > _pawn_attack_squares;
	vector<vector<vector<uint8_t> > > _pawn_move_squares;

	_AttackSquares();

};