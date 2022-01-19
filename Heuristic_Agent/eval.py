import random
import chess
from math import inf, copysign
from score import Score


piece_values = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3, chess.ROOK: 5, chess.QUEEN: 9, chess.KING: 0}

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
	