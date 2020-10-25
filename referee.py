import chess
import chess.svg
import math
import random
from multiprocessing import Pool, cpu_count

class Referee :
	
	@staticmethod
	def run_match(p1, p2) :
		print("starting a game")
		# white and black randomly selected
		board = chess.Board()
		if random.randint(0,1) :
			player_color = {chess.WHITE: p1, chess.BLACK: p2}
		else :
			player_color = {chess.WHITE: p2, chess.BLACK: p1}

		moves = 0
		while not board.is_game_over() :
			move = player_color[board.turn].get_move(board, board.turn)
			assert move in board.legal_moves
			print(move)
			board.push(move)
			moves += 1
			if board.can_claim_fifty_moves() :
				print("\tDraw: Fifty moves")
				break
		print("\t", board.is_game_over(), board.is_variant_draw())
		result = board.result(claim_draw=True)
		print("\t", board.fen)
		assert result != "*", "Referee declared game over before it ended"
		print("\t", board.is_game_over(), board.is_variant_draw())
		if result == "1-0" :
			print("\tWin: White", moves)
			return player_color[chess.WHITE]
		elif result == "0-1" :
			print("\tWin: Black", moves)
			return player_color[chess.BLACK]
		else :
			print("\tDraw: Tie", result, moves)
			return player_color[chess.BLACK] # we'll say black wins if it is a draw

	# returns the ranks of the agents in a dictionary - most scores are ties
	@staticmethod
	def run_bracket(agents) :
		print("Starting a bracket")
		assert math.log2(len(agents)) % 1 == 0

		ranks = { a: math.log2(len(agents)) for a in agents }

		n = len(agents)
		new_agents = []

		while len(agents) > 1 :
			for i in range(0, len(agents), 2) :
				winner = Referee.run_match(agents[i], agents[i + 1])
				ranks[winner] -= 1
				new_agents.append(winner)
			agents = new_agents
			new_agents = []

		return ranks

	def __init__(self) :
		self.pool = Pool(processes=1)
		# self.pool = Pool(processes=cpu_count())

	def get_ranks(self, agents, num_rounds) :
		bracket_seedings = []
		for _ in range(num_rounds) :
			new_agents = agents.copy()
			random.shuffle(new_agents)
			bracket_seedings.append(new_agents)

		ranks = self.pool.map(Referee.run_bracket, bracket_seedings)
		agent_ranks = [ mean([ d[a] for d in ranks ]) for a in agents ]
		return agent_ranks
		
	






