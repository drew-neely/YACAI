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

namespace {

constexpr uint8_t kPuzzleSearchDepth = 4;

string move_to_uci(const Move& move) {
    string uci(square_name(move.from_square));
    uci += square_name(move.to_square);
    if(move.move_type == MOVE_PROMOTE) {
        switch(move.promotion_type) {
            case QUEEN : uci += 'q'; break;
            case ROOK  : uci += 'r'; break;
            case BISHOP: uci += 'b'; break;
            case KNIGHT: uci += 'n'; break;
            default    : break;
        }
    }
    return uci;
}

bool moves_equal(const Move& lhs, const Move& rhs) {
    if(lhs.from_square != rhs.from_square || lhs.to_square != rhs.to_square || lhs.move_type != rhs.move_type) {
        return false;
    }
    if(lhs.move_type == MOVE_CASTLE) {
        return lhs.castle_direction == rhs.castle_direction;
    } else if(lhs.move_type == MOVE_ENPASS) {
        return lhs.enpass_capture_square == rhs.enpass_capture_square;
    } else if(lhs.move_type == MOVE_PROMOTE) {
        return lhs.promotion_type == rhs.promotion_type;
    }
    return true;
}

bool move_is_legal(Board& board, const Move& target) {
    MoveGenerator legal = board.legalMoves();
    for(Move move : legal) {
        if(moves_equal(move, target)) {
            return true;
        }
    }
    return false;
}

void report_search_failure(size_t puzzle_idx, Board& board, size_t ply_index,
                           const Move& expected, const MinimaxMaterial::MinimaxScore_t& score) {
    printf("Puzzle %zu failed at ply %zu\n", puzzle_idx + 1, ply_index + 1);
    printf("  FEN           : %s\n", board.get_fen().c_str());
    printf("  Expected move : %s\n", move_to_uci(expected).c_str());
    printf("  Minimax move  : %s (score=%d, mate_in=%d, depth=%d)\n",
           move_to_uci(score.bestMove).c_str(), score.score, score.mate_in, score.depth);
}

void report_forced_move_failure(size_t puzzle_idx, Board& board, size_t ply_index,
                                const Move& move) {
    printf("Puzzle %zu failed at ply %zu\n", puzzle_idx + 1, ply_index + 1);
    printf("  Forced move   : %s\n", move_to_uci(move).c_str());
    printf("  Reason        : move is illegal in position %s\n", board.get_fen().c_str());
}

} // namespace

void run_puzzle_tests(string filename) {
    MinimaxMaterial minimax;
    minimax.setDepth(kPuzzleSearchDepth);
    vector<PuzzleTest> tests = get_puzzle_tests(filename);

    size_t solved = 0;
    size_t failed = 0;
    size_t skipped = 0;

    for(size_t idx = 0; idx < tests.size(); idx++) {
        const PuzzleTest& test = tests[idx];
        Board board(test.fen);
        bool puzzle_failed = false;
        bool agent_had_move = false;
        size_t agent_move_count = 0;

        for(size_t ply = 0; ply < test.solution.size(); ply++) {
            Move expected = test.solution[ply];
            expected.build_context(board);

            if((ply & 1U) == 0) { // inactive color plays scripted move
                if(!move_is_legal(board, expected)) {
                    report_forced_move_failure(idx, board, ply, expected);
                    puzzle_failed = true;
                    break;
                }
                board.makeMove(expected);
            } else { // active color should match minimax output
                if(game_end(board.state->game_end_reason)) {
                    printf("Puzzle %zu failed at ply %zu\n", idx + 1, ply + 1);
                    printf("  Reason        : position already ended before search turn\n");
                    puzzle_failed = true;
                    break;
                }
                agent_had_move = true;
                auto score = minimax.search(board);
                Move bestMove = score.bestMove;
                if(!moves_equal(bestMove, expected)) {
                    report_search_failure(idx, board, ply, expected, score);
                    puzzle_failed = true;
                    break;
                }
                board.makeMove(bestMove);
                agent_move_count++;
            }
        }

        if(puzzle_failed) {
            failed++;
        } else if(!agent_had_move) {
            skipped++;
        } else {
            printf("Puzzle %zu passed: %s\n", idx + 1, board.get_fen().c_str());
            solved++;
        }
    }

    printf("Puzzle summary: %zu solved, %zu failed, %zu skipped (depth=%u)\n",
           solved, failed, skipped, kPuzzleSearchDepth);
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
