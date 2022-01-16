import sys, os
from timeit import default_timer as timer
import chess
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent import extractors



def DFS_search() :
	board = chess.Board()
	for move1 in board.legal_moves :
		board.push(move1)
		for move2 in board.legal_moves :
			board.push(move2)
			for move3 in board.legal_moves :
				board.push(move3)
				board.pop()
			board.pop()
		board.pop()

def DFS_search_eval() :
	board = chess.Board()
	for move1 in board.legal_moves :
		board.push(move1)
		for move2 in board.legal_moves :
			board.push(move2)
			# for move3 in board.legal_moves :
				# board.push(move3)
			features = [e.extract(board, chess.WHITE) for e in extractors]
				# board.pop()
			board.pop()
		board.pop()



N = 1
if __name__ == "__main__" :
	funcs = [DFS_search, DFS_search_eval]
	result = [0] * len(funcs)
	for i in range(len(funcs)):
		for _ in range(N) :
			start = timer()
			funcs[i]()
			end = timer()
			result[i] += end - start
			print("AYE")
	result = [res / N for res in result]
	for i in range(len(funcs)):
		print(funcs[i].__name__,"\t", result[i])
	print("percent diff\t", (result[1] - result[0]) / result[0] * 100)
	print()
	for e in extractors :
		print(e.__class__.__name__, "\t", e.time_running / result[1] * 100)
