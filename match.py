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
		self.white_id = white.id
		self.black_id = black.id
		self.winner_id = winner.id if winner != None else None
		self.moves = ' '.join([move.uci() for move in board.move_stack])
		self.perf_data = [e.time_running for e in extractors]

class Match :

	def __init__(self, white, black, random_colors=False) :
		# if random_color then do random assignment of colors - else randomize it
		if random_colors and random.randint(0,1) :
			self.players = {chess.WHITE: black, chess.BLACK: white}
		else :
			self.players = {chess.WHITE: white, chess.BLACK: black}

	def is_game_end(self, board) :
		w = b = 0
		for sq in chess.SQUARES :
			p = board.piece_at(sq)
			if p != None :
				if p.color == chess.BLACK:
					b += 1
				elif p.color == chess.WHITE:
					w += 1

		return board.is_game_over() or w == 1 or b == 1

	def run(self) :
		# !!! Add logic to determine cause of game end - especially for draws

		# init board
		self.board = chess.Board()
		
		# conduct game
		moves = 0 
		while not self.is_game_end(self.board) :
			move = self.players[self.board.turn].get_move(self.board, self.board.turn)
			self.board.push(move)
			moves += 1
			if self.board.can_claim_fifty_moves() :
				break
		
		# get result
		result = self.board.result(claim_draw=True)

		# return result
		if result == "1-0" :
			print("\tWin: White - moves: ", moves)
			winner = self.players[chess.WHITE]
		elif result == "0-1" :
			print("\tWin: Black - moves: ", moves)
			winner = self.players[chess.BLACK]
		else :
			pd = PointDifference()
			diff = pd.extract(self.board, chess.WHITE)[0]
			if diff > 0 :
				print("\tUnfinished game: White gets the win - moves: ", moves, ", pd: ", abs(diff))
				winner = self.players[chess.WHITE]
			else :
				print("\tUnfinished game: Black gets the win - moves: ", moves, ", pd: ", abs(diff))
				winner = self.players[chess.BLACK]
		res = Result(self.players[chess.WHITE], self.players[chess.BLACK], winner, self.board)
		return res