#pragma once

#include <stdint.h>
#include <stdio.h>
#include <vector>

struct _AttackSquares;
extern _AttackSquares AttackSquares;
#include "board.h"

using namespace std;

struct _AttackSquares {
	
	vector<vector<vector<vector<uint8_t> > > > attack_squares;
	vector<vector<vector<uint8_t> > > pawn_attack_squares;
	vector<vector<vector<uint8_t> > > pawn_move_squares;

	_AttackSquares();

};