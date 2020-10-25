import chess
import chess.svg
import math
import random
from multiprocessing import Pool, cpu_count
from statistics import mean
from featureExtraction import PointDifference

class Referee :

	@staticmethod
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
	
	@staticmethod
	def run_match(p1, p2) :
		# white and black randomly selected
		board = chess.Board()
		if random.randint(0,1) :
			player_color = {chess.WHITE: p1, chess.BLACK: p2}
		else :
			player_color = {chess.WHITE: p2, chess.BLACK: p1}

		moves = 0
		while not Referee.is_game_end(board) :
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
			return player_color[chess.WHITE]
		elif result == "0-1" :
			print("\tWin: Black - moves: ", moves)
			return player_color[chess.BLACK]
		else :
			pd = PointDifference()
			diff = pd.extract(board, chess.WHITE)[0]
			if diff > 0 :
				print("\tUnfinished game: White gets the win - moves: ", moves, ", pd: ", abs(diff))
				return player_color[chess.WHITE]
			else :
				print("\tUnfinished game: Black gets the win - moves: ", moves, ", pd: ", abs(diff))
				return player_color[chess.BLACK]

	def __init__(self) :
		# self.pool = Pool(processes=1)
		self.pool = Pool(processes=cpu_count())

	# returns the ranks of the agents in a dictionary - most scores are ties
	@staticmethod
	def run_bracket(agents) :
		print("Starting a bracket")
		assert math.log2(len(agents)) % 1 == 0
		ranks = { a.id : math.log2(len(agents)) for a in agents }

		n = len(agents)
		new_agents = []

		while len(agents) > 1 :
			for i in range(0, len(agents), 2) :
				winner = Referee.run_match(agents[i], agents[i + 1])
				ranks[winner.id] -= 1
				new_agents.append(winner)
			agents = new_agents
			new_agents = []

		return ranks

	def get_ranks(self, agents, num_rounds) :
		bracket_seedings = []
		for _ in range(num_rounds) :
			new_agents = agents.copy()
			random.shuffle(new_agents)
			bracket_seedings.append(new_agents)

		ranks = self.pool.map(Referee.run_bracket, bracket_seedings)
		agent_ranks = [ mean([ d[a.id] for d in ranks ]) for a in agents ]
		return agent_ranks
		
	