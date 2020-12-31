import chess
from featureExtraction import PointDifference
import random
from agent import extractors

class Result :
	# arguments:
	#	white, black -> the white and black agents
	#	winner       -> the winning agent or None for a draw
	#	board        -> the resultant board
	def __init__(self, white, black, winner, board):
		self.white = white
		self.black = black
		self.winner = winner
		self.moves = ' '.join([move.uci() for move in board.move_stack])
		self.perf_data = [e.time_running for e in extractors]

def is_game_end(board) :
	w = b = 0
	for sq in chess.SQUARES :
		p = board.piece_at(sq)
		if p != None :
			if p.color == chess.BLACK:
				b += 1
			elif p.color == chess.WHITE:
				w += 1

	return board.is_game_over() or w == 1 or b == 1
	
def run_match(p1, p2) :
	# white and black randomly selected
	board = chess.Board()
	if random.randint(0,1) :
		player_color = {chess.WHITE: p1, chess.BLACK: p2}
	else :
		player_color = {chess.WHITE: p2, chess.BLACK: p1}

	moves = 0
	while not is_game_end(board) :
		move = player_color[board.turn].get_move(board, board.turn)
		assert move in board.legal_moves
		board.push(move)
		moves += 1
		if board.can_claim_fifty_moves() :
			break
	result = board.result(claim_draw=True)
	# assert result != "*", "Referee declared game over before it ended"
	if result == "1-0" :
		print("\tWin: White - moves: ", moves)
		winner = player_color[chess.WHITE]
	elif result == "0-1" :
		print("\tWin: Black - moves: ", moves)
		winner = player_color[chess.BLACK]
	else :
		pd = PointDifference()
		diff = pd.extract(board, chess.WHITE)[0]
		if diff > 0 :
			print("\tUnfinished game: White gets the win - moves: ", moves, ", pd: ", abs(diff))
			winner = player_color[chess.WHITE]
		else :
			print("\tUnfinished game: Black gets the win - moves: ", moves, ", pd: ", abs(diff))
			winner = player_color[chess.BLACK]
	res = Result(player_color[chess.WHITE], player_color[chess.BLACK], winner, board)
	return res