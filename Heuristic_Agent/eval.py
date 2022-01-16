import random
import chess
from math import inf, copysign


piece_values = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3, chess.ROOK: 5, chess.QUEEN: 9, chess.KING: 0}
outcome_values = {chess.WHITE: 999999, chess.BLACK: -999999, None: 0}

# returns (<points of white material>, <points of black material>)
def points(board) :
	w = b = 0
	for sq in chess.SQUARES :
		p = board.piece_at(sq)
		if p != None :
			if p.color == chess.WHITE :
				w += piece_values[p.piece_type]
			else :
				b += piece_values[p.piece_type]
	return (w,b)


######################################################

def get_eval(board) :
	outcome = board.outcome(claim_draw = True)
	if outcome != None :
		return outcome_values[outcome.winner]
	w_mat, b_mat = points(board)
	return w_mat-b_mat
	