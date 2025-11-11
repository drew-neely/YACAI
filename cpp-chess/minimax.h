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
        auto mate_rank = [](int8_t mate) {
            if(mate > 0) return 2;
            if(mate == 0) return 1;
            return 0;
        };

        int self_rank = mate_rank(mate_in);
        int other_rank = mate_rank(other.mate_in);
        if(self_rank != other_rank) {
            return self_rank < other_rank;
        }

        if(self_rank == 1) { // neither is mate
            return score < other.score;
        }

        // For mates (either white or black) smaller |mate_in| is better
        return mate_in > other.mate_in;
    }

    bool operator>(const Score<Eval_t>& other) const {
        return other < *this;
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

    // stats
    uint64_t leaf_nodes;
    uint64_t moves_generated;
    uint64_t positions_evaled;
    uint64_t table_lookups;

    Minimax() : table(DEFAULT_TRANS_TABLE_SIZE) {}
    Minimax(size_t capacity) : table(capacity) {}

    virtual Eval_t eval(Board& board) = 0;
    
    void setDepth(uint8_t depth) {
        this->search_depth = depth;
    }

    // Implements a depth-limited minimax search with alpha-beta pruning
    MinimaxScore_t search(Board& board) {

        assert(game_end(board.state->game_end_reason) == false); // Cannot search on a leaf node

        leaf_nodes = 0;
        moves_generated = 0;
        positions_evaled = 0;
        table_lookups = 0;

        /*
            Do a first level search
        */
        Score_t score = _search(board, search_depth);
        bool maxing = board.state->turn == WHITE;
        Score_t bestScore;
        Move bestMove;
        MoveGenerator moves = board.legalMoves();
        bool firstIteration = true;
        for(Move move : moves) {
            moves_generated++;
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

        printf("Search stats: leafs %ld, moves %ld, evals %ld, table_lookups %ld\n", leaf_nodes, moves_generated, positions_evaled, table_lookups);

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
            leaf_nodes++;
            if(winner == DRAW) {
                return {0, 0, 0};
            } else if(winner == WHITE) {
                return {0, (int8_t)(search_depth - depth), 0};
            } else if(winner == BLACK) {
                return {0, (int8_t)(-(search_depth - depth)), 0};
            }
            assert(false);

        } else if(table.contains(board.state->zobrist)) {
            Score_t score = table.get(board.state->zobrist);
            if(score.depth >= depth) {
                table_lookups++;
                return score;
            }
        } else if(depth == 0) {
            positions_evaled++;
            return {eval(board), 0, 0};
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
            moves_generated++;
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
        bestScore.depth++;
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
