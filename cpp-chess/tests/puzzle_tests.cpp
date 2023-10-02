#include <stdio.h>
#include <assert.h>
#include <vector>
#include <string>
#include <sstream>
#include <fstream>

#include "../board.h"
#include "../move.h"
#include "../minimax.h"

#include "puzzle-tests.h"

using namespace std;

void run_puzzle_tests(string filename) {
    MinimaxMaterial minimax;
    minimax.setDepth(6);
    vector<PuzzleTest> tests = get_puzzle_tests(filename);
    for(PuzzleTest test : tests) {
        Board board(test.fen);
        test.solution[0].build_context(board);
        board.makeMove(test.solution[0]);
        uint8_t player = board.state->turn;
        auto score = minimax.search(board);
        printf("score = %d, mate_in = %d, depth = %d\n", score.score, score.mate_in, score.depth);
        return;
    }
}

vector<PuzzleTest> get_puzzle_tests(string filename) {
    /*
        Example 2 line:
        r4k1r/1p3p1b/p2Q3p/4pPp1/2q3P1/5N1P/PP3K2/3R4 b - - 1 28
        f8g7 f5f6 g7g8 d6d8 a8d8 d1d8
    */
    string fen_s;
    string solution_s;
    char move_s[6];
    ifstream infile(filename);
	assert(infile.is_open());
    vector<PuzzleTest> tests;
    while(getline(infile, fen_s) && getline(infile, solution_s)) {
        vector <Move> solution;
        uint8_t move_idx = 0;
        for(uint8_t i = 0; i <= solution_s.size(); i++) {
            if(solution_s[i] == ' ' || solution_s[i] == '\0') {
                move_s[move_idx] = '\0';
                solution.push_back(Move(move_s));
                move_idx = 0;
            } else {
                move_s[move_idx] = solution_s[i];
                move_idx++;
                assert(move_idx < 6);
            }
        }
        PuzzleTest test(fen_s.c_str(), solution);
        tests.push_back(test);
    }
    infile.close();
    return tests;
    
}

