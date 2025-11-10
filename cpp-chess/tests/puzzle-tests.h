#pragma once

#include <stdio.h>
#include <assert.h>
#include <vector>
#include <string>

#include "../board.h"
#include "../move.h"

using namespace std;

struct PuzzleTest {

    PuzzleTest(const char* fen, vector<Move> solution) : fen(fen), solution(solution) {}

    string fen;
    vector<Move> solution;

};

void run_puzzle_tests(string filename);

vector<PuzzleTest> get_puzzle_tests(string filename);