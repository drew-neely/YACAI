#pragma once

#include <stdio.h>
#include <assert.h>

#include "../board.h"
#include "../move.h"

struct GameEndTest {
	uint8_t end_reason;
	vector<Move> moves;
};



void run_game_end_tests(string filename);

vector<GameEndTest> get_game_end_tests(string filename);
