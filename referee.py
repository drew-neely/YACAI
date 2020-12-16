import chess
import chess.svg
import math
import random
from multiprocessing import cpu_count, Process, Queue
from statistics import mean
from featureExtraction import PointDifference

def worker(match_queue, result_queue) :
		while True :
			(agent1, agent2, i, level, round) = match_queue.get()
			winner = Referee.run_match(agent1, agent2)
			result_queue.put((winner, i, level + 1, round))

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
		self.match_queue = Queue()    # format (a1, a2, i, l, r)
		self.result_queue = Queue()   # format (winner, i, l, r)
		self.workers = [Process(target=worker, args=(self.match_queue, self.result_queue), daemon=True) for _ in range(cpu_count())]
		for w in self.workers :
			w.start()

	def __del__(self) :
		for w in self.workers :
			w.terminate()
		for w in self.workers :
			# wait for process to die - doesn't happen immediately on terminate
			while w.is_alive() :
				pass
			w.close()


	# rank calculated by average placement in bracket -
	# 	One is subtracted for each win and at the end the number of rounds is divided out
	def get_ranks(self, agents, num_rounds) :
		assert math.log2(len(agents)) % 1 == 0 and len(agents) > 1 and num_rounds > 1

		ranks = {a.id : math.log2(len(agents)) * num_rounds for a in agents}
		# bracket_seedings stores num_rounds arrays that contain the positions of agents
		#     at every level of the brackets - (ie. [[[a1, a2, a3, a4], [a1, a4], [a4]], ...])
		#     Initialized to None for all but first level of each bracket
		bracket_seedings = []

		# initialize brackets and assign initial matches to workers
		for round in range(num_rounds) :
			new_agents = agents.copy()
			random.shuffle(new_agents)
			bracket_seedings.append([new_agents] + [[None] * (2 ** x) for x in range(int(math.log2(len(agents)))-1,-1,-1)])
			for i in range(0, len(agents), 2):
				self.match_queue.put((new_agents[i], new_agents[i+1], int(i/2), 0, round))

		# listen for matches results, adjust rank, and schedule next match until all results are in
		expected_matches = (len(agents) - 1) * num_rounds
		max_level = math.log2(len(agents))
		num_matches = 0
		while num_matches < expected_matches :
			(winner, i, level, round) = self.result_queue.get()
			ranks[winner.id] -= 1
			print("(r l i) = (", round, level, i, ")")
			print("matches left =", expected_matches - num_matches)
			bracket_seedings[round][level][i] = winner
			if level != max_level : # final winner of bracket
				opponent = bracket_seedings[round][level][i - 2 * (i%2) + 1] # last index is equation to get paired index
				if opponent != None :
					self.match_queue.put((winner, opponent, int(i/2), level, round))
			num_matches += 1

		ranks = [ ranks[a.id] / num_rounds for a in agents ]
		return ranks
		
	