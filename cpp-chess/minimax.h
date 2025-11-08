#pragma once

#include <stdint.h>
#include <stdio.h>
#include <cmath>
#include <vector>
#include <assert.h>
#include <string.h>

#include "board.h"
#include "move.h"
#include "chess_containers.h"


#define DEFAULT_TRANS_TABLE_SIZE 0x100000   // 1,048,576

/*
    MinimaxScore represents the intermediate results of the minimax search
*/
template <class Eval_t>
struct Score {
    Eval_t score;
    int8_t mate_in; // 0 for no mate, positive for white mate, negative for black mate
    uint8_t depth;

    bool operator<(const Score<Eval_t>& other) const {
        if(mate_in == 0 && other.mate_in == 0) { // neither score is mate
            return score < other.score;
        } else if(mate_in > 0 && other.mate_in > 0) { // both scores are white mate
            return mate_in > other.mate_in;
        } else { // one score is mate and the other is not, or both scores are black mate
            return mate_in < other.mate_in;
        }
    }

    bool operator>(const Score<Eval_t>& other) const {
        if(mate_in == 0 && other.mate_in == 0) { // neither score is mate
            return score > other.score;
        } else if(mate_in < 0 && other.mate_in < 0) { // both scores are black mate
            return mate_in < other.mate_in;
        } else { // one score is mate and the other is not, or both scores are white mate
            return mate_in > other.mate_in;
        }
    }
};

/*
    Score is the final evaluation result of the minimax search
*/
template <class Eval_t>
struct MinimaxScore : Score<Eval_t> {
    Move bestMove;
};

/*
    Abstract class to be subclassed with specific implementation of eval function
*/
template <class Eval_t>
class Minimax {
public:
    using Score_t = Score<Eval_t>;
    using MinimaxScore_t = MinimaxScore<Eval_t>;

    TransTable<Score_t> table;
    uint8_t search_depth;

    Minimax() : table(DEFAULT_TRANS_TABLE_SIZE) {}
    Minimax(size_t capacity) : table(capacity) {}

    virtual Eval_t eval(Board& board) = 0;
    
    void setDepth(uint8_t depth) {
        this->search_depth = depth;
    }

    // Implements a depth-limited minimax search with alpha-beta pruning
    MinimaxScore_t search(Board& board) {

        assert(game_end(board.state->game_end_reason) == false); // Cannot search on a leaf node

        /*
            Do a first level search
        */
        bool maxing = board.state->turn == WHITE;
        Score_t bestScore;
        Move bestMove;
        MoveGenerator moves = board.legalMoves();
        bool firstIteration = true;
        for(Move move : moves) {
            board.makeMove(move);
            Score_t score = _search(board, search_depth - 1);
            if(firstIteration) {
                bestScore = score;
                bestMove = move;
                firstIteration = false;
            } else if((maxing && score > bestScore) || (!maxing && score < bestScore)) {
                bestScore = score;
                bestMove = move;
            }
            board.unmakeMove();
        }
        assert(!firstIteration); // There should always be at least one move

        /*
            Build the final result
        */
        MinimaxScore_t minimaxScore;
        minimaxScore.score = bestScore.score;
        minimaxScore.mate_in = bestScore.mate_in;
        minimaxScore.depth = bestScore.depth;
        minimaxScore.bestMove = bestMove;
        return minimaxScore;
    }

    Score_t _search(Board& board, uint8_t depth) {
        /*
            Handle leaf nodes - game end, transposition table lookup, or depth limit
        */
        MoveGenerator fake_moves = board.legalMoves();
        for(Move move : fake_moves) {}
        if(game_end(board.state->game_end_reason)) {
            uint8_t winner = winner(board.state->game_end_reason);
            if(winner == DRAW) {
                return {0, 0, (uint8_t)(search_depth - depth)};
            } else if(winner == WHITE) {
                return {0, (int8_t)(search_depth - depth), (uint8_t)(search_depth - depth)};
            } else if(winner == BLACK) {
                return {0, (int8_t)(-(search_depth - depth)), (uint8_t)(search_depth - depth)};
            }
            assert(false);
        } else if(table.contains(board.state->zobrist)) {
            Score_t score = table.get(board.state->zobrist);
            if(score.depth >= depth) {
                return score;
            }
        } else if(depth == 0) {
            return {eval(board), 0, search_depth};
        }

        /*
            Search the tree
        */
        bool maxing = board.state->turn == WHITE;
        Score_t bestScore;
        MoveGenerator moves = board.legalMoves();
        // printf("%s\n", board.get_fen().c_str());
        bool firstIteration = true;
        for(Move move : moves) {
            // printf("makeMove :");
            // move.print();
            board.makeMove(move);
            Score_t score = _search(board, depth - 1);
            if(firstIteration) {
                bestScore = score;
                firstIteration = false;
            } else if((maxing && score > bestScore) || (!maxing && score < bestScore)) {
                bestScore = score;
            }
            // printf("unMove   :");
            // move.print();
            board.unmakeMove();
        }
        if(firstIteration) {
            printf("No moves found\n");
            printf("game end = %d\n", game_end(board.state->game_end_reason));
        }
        assert(!firstIteration); // There should always be at least one move
        table.set(board.state->zobrist, bestScore);
        return bestScore;
    }

};

/*
    Implementation of Minimax which evaluates the point value of the pieces on the board
*/
class MinimaxMaterial : public Minimax<uint16_t> {
public:
    MinimaxMaterial() : Minimax<uint16_t>() {}
    MinimaxMaterial(size_t capacity) : Minimax<uint16_t>(capacity) {}

    uint16_t eval(Board& board) {
        Composition comp = board.state->composition;
        uint16_t score = 0;
        score += comp.getNumPieces(WHITE | PAWN);
        score += comp.getNumPieces(WHITE | KNIGHT) * 3;
        score += comp.getNumPieces(WHITE | BISHOP) * 3;
        score += comp.getNumPieces(WHITE | ROOK) * 5;
        score += comp.getNumPieces(WHITE | QUEEN) * 9;
        score -= comp.getNumPieces(BLACK | PAWN);
        score -= comp.getNumPieces(BLACK | KNIGHT) * 3;
        score -= comp.getNumPieces(BLACK | BISHOP) * 3;
        score -= comp.getNumPieces(BLACK | ROOK) * 5;
        score -= comp.getNumPieces(BLACK | QUEEN) * 9;
        return score;
    }
};