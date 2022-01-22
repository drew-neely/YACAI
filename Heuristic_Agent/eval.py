import random
from turtle import color
import chess
from math import inf, copysign
from score import Score


piece_values = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3, chess.ROOK: 5, chess.QUEEN: 9, chess.KING: 0}

pawn_dist_multiplier = 1.05
passed_pawn_multiplier = 1.2
boxed_out_passed_pawn_multiplier = 3

# returns (<points of white material>, <points of black material>)
def points(board) :
	w = b = 0
	for sq in chess.SQUARES :
		p = board.piece_at(sq)
		if p != None :
			is_white = p.color == chess.WHITE
			if p.piece_type == chess.PAWN :
				file, rank = chess.square_file(sq), chess.square_rank(sq)
				dist_traveled = (rank - 1) if is_white else (6 - rank)
				pv = piece_values[chess.PAWN] * (pawn_dist_multiplier ** dist_traveled)
				ahead_ranks = range(rank+1,7) if is_white else range(1, rank)
				ahead_squares = [chess.square(f, r) for r in ahead_ranks for f in range(max(file-1, 0), min(file+1, 7))]
				passed_pawn = True
				for asq in ahead_squares :
					ap = board.piece_at(asq)
					if ap != None and ap.piece_type == chess.PAWN and ap.color != p.color :
						passed_pawn = False
						break
				if passed_pawn :
					pv *= passed_pawn_multiplier

			else :
				pv = piece_values[p.piece_type]
			
			
			if is_white : 
				w += pv
			else : 
				b += pv

	return (w,b)


######################################################

def get_eval(board) :
	outcome = board.outcome(claim_draw = True)
	if outcome :
		if outcome.winner == chess.WHITE :
			return Score.checkmate(chess.WHITE)
		elif outcome.winner == chess.BLACK :
			return Score.checkmate(chess.BLACK)
		else : 
			return Score.draw()
	w_mat, b_mat = points(board)
	score = Score.score(w_mat - b_mat)
	return score

	