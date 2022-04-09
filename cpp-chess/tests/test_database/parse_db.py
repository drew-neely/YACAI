import os
import bz2
import gzip
import argparse
import chess
import chess.pgn

###############################
####### handle arguments
###############################

parser = argparse.ArgumentParser()
parser.add_argument('path_to_db', type=str, help='path to the lichess database download')
parser.add_argument('-o', '--output', type=str, help='name of output file')

args = parser.parse_args()

if args.output is None :
	args.output = os.path.splitext(args.path_to_db)[0]
	if args.output[-4:] == ".pgn" :
		args.output += ".list"
	else :
		args.output += ".pgn.list"

print(args)

###############################
####### setup input/output files
###############################

# input file setup
if os.path.splitext(args.path_to_db)[1] == ".gz" :
	pgn = gzip.open(args.path_to_db, "rt") # read as text to be compatible with chess.pgn
elif os.path.splitext(args.path_to_db)[1] == ".bz2" :
	pgn = bz2.open(args.path_to_db, "rt") # read as text to be compatible with chess.pgn
else :
	pgn = open(args.path_to_db, "r")

# output file setup
out = open(args.output, "w")

###############################
####### parse games
###############################

def game_status(board) :
	# want to ignore the super specific rule that three fold repitition occurs when there is a repeated posisition posible after the next move
	if board.is_repetition() or board.is_fifty_moves() or board.is_insufficient_material() or board.is_checkmate() or board.is_stalemate() :
		outcome = board.outcome(claim_draw=True)
		assert outcome is not None
		return outcome
	return None

while True :
	game = chess.pgn.read_game(pgn)
	if game is None : # check to see if we reached the end of the list
		break
	if game.headers["Termination"] == "Time forfeit" :
		continue

	board = chess.Board()
	for n in game.mainline() :
		board.push(n.move)
		outcome = game_status(board)
		if outcome is not None :
			break
	if outcome and outcome.termination != chess.Termination.FIVEFOLD_REPETITION : # check that outcome exists and that it is not fivefold repitition (lichess was weird for at least one game and didn't force a draw)
		termination_reason = outcome.termination.name.lower()
		winner = {True: "white", False: "black", None: "draw"}[outcome.winner]
		moves = ' '.join([m.uci() for m in board.move_stack])
		if len(moves) == 0 :
			print("game with 0 moves")
			print(game)
		else :
			out.write(termination_reason + '\n')
			out.write(winner + '\n')
			out.write(moves + '\n')


###############################
####### teardown
###############################

pgn.close()
out.close()