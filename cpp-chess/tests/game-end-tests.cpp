#include <stdio.h>
#include <assert.h>
#include <vector>
#include <string>
#include <sstream>
#include <fstream>
#include <algorithm>

#include "../board.h"
#include "../move.h"
#include "../zobrist.h"

#include "game-end-tests.h"

using namespace std;

/*
	When comparing against other chess engines for valididty, some follow
	FIDE rules, not USCF 
	    * FIDE - two nights vs lone king is not insufficient material (lichess)
		* USCF - two nights vs lone king is insufficient material (chess.com)
		* FIDE - bishop vs knight is not insufficient material (lichess)
		* USCF - bishop vs knight is insufficient material (chess.com)
	This function is used to identify when this draw has occured with as few dependencies on other code being correct as possible.
*/
bool is_edge_case_draw(Board board) {
	uint8_t white_knight = 0;
	uint8_t black_knight = 0;
	uint8_t white_bishop = 0;
	uint8_t black_bishop = 0;
	if(board.state->game_end_reason != INSUFICIENT_MATERIAL) 
		return false;
	for(int i = 0; i < 64; i++) {
		uint8_t pid = board.state->squares[i];
		if(pid == 0 || piece(pid) == KING) {
			continue;
		} else if(piece(pid) == KNIGHT) {
			if(color(pid) == WHITE) {
				white_knight += 1;
			} else if(color(pid) == BLACK) {
				black_knight += 1;
			}
		} else if(piece(pid) == BISHOP) {
			if(color(pid) == WHITE) {
				white_bishop += 1;
			} else if(color(pid) == BLACK) {
				black_bishop += 1;
			}
		} else {
			return false;
		}
	}
	if(((white_knight == 2 && black_knight == 0) || (white_knight == 0 && black_knight == 2)) && (white_bishop == 0 && black_bishop == 0)) {
		// printf("KNNk draw found\n");
		return true;
	} else if((white_bishop == 1 && black_bishop == 0 && white_knight == 0 && black_knight == 1) || (white_bishop == 0 && black_bishop == 1 && white_knight == 1 && black_knight == 0)) {
		// printf("KBkn draw found\n");
		return true;
	} else if((white_knight == 1 && black_knight == 1) && (white_bishop == 0 && black_bishop == 0)) {
		// printf("KNkn draw found\n");
		return true;
	} else {
		return false;
	}
}

const std::map<uint8_t, string> winner_str = {
	{WHITE, "white"},
	{BLACK, "black"},
	{DRAW, "draw"}
};
const std::map<uint8_t, string> reason_str = {
	{CHECKMATE, "checkmate"},
	{STALEMATE, "stalemate"},
	{REPITION, "threefold_repetition"},
	{INSUFICIENT_MATERIAL, "insufficient_material"},
	{FIFTY_MOVE, "fifty_moves"}
};

void run_game_end_tests(string filename) {
	vector<GameEndTest> tests = get_game_end_tests(filename);
	printf("Running %lu tests from %s\n", tests.size(), filename.c_str());
	int num_pass = 0;
	int num_fail = 0;
	for(int i = 0; i < tests.size(); i++) {
		GameEndTest test = tests[i];
		Board board;
		// check moves and get to end position
		for(Move move : test.moves) {
			move.build_context(board);
			vector<Move> legal_moves = board.legalMoves();
			if(find(legal_moves.begin(), legal_moves.end(), move) == legal_moves.end()) {
				// check if this is because of disagreement on lone king vs 2 knights case
				if (is_edge_case_draw(board)) {
					num_pass++;
					goto endtest;
				}
				// Move not in legal moves list
				printf("FAIL : test %d\n", i);
				printf("\tCouldn't find move in legal moves\n");
				printf("\tfen = %s\n", board.get_fen().c_str());
				printf("\tmove = ");
				move.print();
				printf("\tendreason = %d\n", board.state->game_end_reason);
				printf("\tlegal moves (num = %lu) :\n", legal_moves.size());
				for(Move lm : legal_moves) {
					printf("\t");
					lm.print();
				}
				num_fail++;
				goto endtest;
			}
			board.makeMove(move);
		}
		board.legalMoves();
		if(board.state->game_end_reason == test.end_reason) {
			// printf("PASS : test %d\n", i);
			num_pass++;
		} else {
			printf("FAIL : test %d\n", i);
			printf("\tEnd reasons do not match");
			printf("\tfen = %s\n", board.get_fen().c_str());
			printf("\texpected reason : %d (winner : %s, reason : %s)\n", test.end_reason, winner_str.at(winner(test.end_reason)).c_str(), reason_str.at(reason(test.end_reason)).c_str());
			printf("\tactual reason   : %d (winner : %s, reason : %s)\n", board.state->game_end_reason, winner_str.at(winner(board.state->game_end_reason)).c_str(), reason_str.at(reason(board.state->game_end_reason)).c_str());
			num_fail++;
		}
		endtest:;
	}
	printf("%d/%d\n", num_pass, num_pass + num_fail);
	printf("%s\n", num_fail == 0 ? "PASS" : "FAIL");
}



const std::map<string, uint8_t> winner_code = {
	{"white", WHITE},
	{"black", BLACK},
	{"draw", DRAW}
};
const std::map<string, uint8_t> reason_code = {
	{"checkmate", CHECKMATE},
	{"stalemate", STALEMATE},
	{"threefold_repetition", REPITION},
	{"insufficient_material", INSUFICIENT_MATERIAL},
	{"fifty_moves", FIFTY_MOVE}
};

vector<GameEndTest> get_game_end_tests(string filename) {
	vector<GameEndTest> tests;
	string reason;
	string winner;
	string uci_moves;
	ifstream infile(filename);
	assert(infile.is_open());
	while(getline(infile, reason) && getline(infile, winner) && getline(infile, uci_moves)) {
		assert(winner_code.count(winner) && reason_code.count(reason));
		uint8_t end_reason = winner_code.at(winner) | reason_code.at(reason);
		vector<Move> moves;
		size_t pos = 0;
		size_t space;
		do {
			space = uci_moves.find(" ", pos);
			moves.emplace_back(uci_moves.substr(pos, space - pos));
			pos = space + 1;
		} while (space != string::npos);
		tests.push_back({ end_reason, moves });
	}
	return tests;
}