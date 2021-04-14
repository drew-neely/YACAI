from timer import Timer
from big_array import BigArray
from tablebase import Tablebase
import chess
import unmove_generator # add unmove functions to chess.Board

start_fen = "rnbqkbnr/8/8/8/8/8/8/RNBQKBNR w - - 0 1"
end_fen = "rn1q2nr/2k5/b7/2b4R/2B5/B1N2Q2/4N3/3RK3 w - - 14 8"

moves = "Nc3 Kf7 Qf3+ Ke6 Bc4+ Ke5 Ba3 Bc5 Nge2 Ba6 Rh5+ Kd6 Rd1+ Kc7".split()

board = chess.Board(start_fen)
for m in moves :
	board.push_san(m)
moves = board.move_stack
print(moves)
board = chess.Board(end_fen)

for i in reversed(range(len(moves))) :
	move = moves[i]
	print(f"\nmove {i} : {move}")
	print(board)
	unmoves = board.unmoves
	print(f"\tunmoves: {[m.uci() for m in unmoves]}")
	if not move in unmoves :
		print("\tunmove not found")
		exit()
	board.unpush(move)
	print(board.fen())

print(board)

Timer.start() 
arr = BigArray('test', 1 << 20)
Timer.end("Array creation")

Timer.start()
for i in range(len(arr)) :
	arr[i] = 98
Timer.end("Array filling")

Timer.start()
arr.flush()
Timer.end("Array writing")