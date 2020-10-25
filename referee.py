import chess
import math
import random
import multiprocessing import Pool, cpu_count

class Referee :
	
	@staticmethod
	def run_match(p1, p2) :

		# white and black randomly selected
		board = chess.Board()
		if random.randint(0,1) :
			player_color = {chess.WHITE: p1, chess.BLACK: p2}
		else :
			player_color = {chess.WHITE: p2, chess.BLACK: p1}

		while not board.is_game_over() :
			move = player_color[board.turn].get_move(board, board.turn)
			assert move in board.legal_moves
			board.push(move)
			if board.can_claim_fifty_moves() :
				break
		
		result = board.result(True)

		assert result != "*", "Referee declared game over before it ended"
		if result == "1-0" :
			return player_color[chess.WHITE]
		elif result == "0-1" :
			return player_color[chess.BLACK]
		else :
			return None

	# returns the ranks of the agents in a dictionary - most scores are ties
	@staticmethod
	def run_bracket(agents) :
		assert math.log2(len(agents)) % 1 == 0

		ranks = { a: math.log2(len(agents)) for a in agents }

		n = len(agents)
		new_agents = []

		while len(agents) > 1
			for i in range(0, len(agents), 2) :
				winner = Referee.run_match(agents[i], agents[i + 1])
				ranks[winner] -= 1
				new_agents.append(winner)
			agents = new_agents
			new_agents = []

		return ranks

	def __init__(self) :
		self.pool = Pool(processes=cpu_count())

	def get_ranks(self, agents, num_rounds) :
		bracket_seedings = []
		for _ in range(num_rounds) :
			new_agents = agents.copy()
			random.shuffle(new_agents)
			bracket_seedings.append(new_agents)

		ranks = self.pool.map(Referee.run_bracket, bracket_seedings)
		agent_ranks = [ mean([ d[a] for d in ranks ]) for a in agents ]
		return agent_ranks
		
	






