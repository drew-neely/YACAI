import os
import bz2
import gzip
import argparse
import chess
import chess.pgn
from collections import Counter

###############################
####### File Format
###############################
"""
Header : (3944 bytes)
	move_table (3944 bytes) - list of max 1972 * 16 bit moves
		move_entry (2 bytes) (little endian)
			- move == 0 -> NULL
			- move[14:15] = promotion type (0 = Queen, 1 = Rook, 2 = Bishop, 3 = Knight) (0 for non-promotion)
			- move[8:13]  = from_square
			- move[6:7]   = 0
			- move[0:5]   = to_square
Body :
	games (undef size) - list of unbounded size
		game_outcome (1 byte)
			- 1 = checkmate white win
			- 2 = checkmate black win
			- 3 = stalemate
			- 4 = threefold_repetition
			- 5 = fifty_moves
			- 6 = insufficient_material
		move_list (undef size)
			move (1 or 2 bytes) (big endian)
				- First byte encodes size - 0b11111XXX -> 2 bytes, else 1 byte
				- 1 byte move value is index into move_table
				- 2 byte move value's least significant 11 bytes is index into move_table
		game_terminator (1 byte) = 0
"""

###############################
####### Util
###############################

prom_type_dict = {'q': 0, 'r': 1, 'b': 2, 'n': 3}
result_codes = {'checkmate':None, 'stalemate': b'\x03', 'threefold_repetition': b'\x04', 'fifty_moves': b'\x05', 'insufficient_material': b'\x06'} # checkmate handled seperately

def open_list(path) :
	if os.path.splitext(path)[1] == ".gz" :
		return gzip.open(path, "rt")
	elif os.path.splitext(path)[1] == ".bz2" :
		return bz2.open(path, "rt")
	else :
		return open(path, "r")

def reason_to_byte(end_reason, winner) :
	if end_reason == "checkmate" :
		return b'\x01' if winner == "white" else b'\x02'
	else :
		return result_codes[end_reason]

def sq_to_int(sq) :
	return (ord(sq[0]) - ord('a')) + 8 * (ord(sq[1]) - ord('1'))

def header_move_to_bytes(move) :
	prom_type = prom_type_dict[move[4]] if len(move) == 5 else 0
	from_square = sq_to_int(move[0:2])
	to_square = sq_to_int(move[2:4])
	code = (prom_type << 14) | (from_square << 8) | (to_square)
	return code.to_bytes(2, 'little')

def index_to_bytes(idx) :
	if idx < 248 : # one byte
		return bytes([idx])
	else : # two bytes
		return (0xF800 | idx).to_bytes(2, 'big')


###############################
####### Analysis
###############################

def analyze(paths) :
	move_counts = Counter()
	for path in paths :
		file = open_list(path)
		content = file.readlines()
		file.close()
		move_counts += Counter(' '.join([line.strip() for (i, line) in enumerate(content) if i % 3 == 2]).split(' '))

	total = sum(move_counts.values())
	n = 247
	most_common = move_counts.most_common(n)
	most_common_total = sum([c for _,c in most_common])
	print(f"The {n} most common moves constitute {most_common_total} out of {total} moves ({most_common_total/total*100:.1f}%)")
	print(f"top 5 moves: {move_counts.most_common(5)}")
	return move_counts

###############################
####### handle arguments
###############################

parser = argparse.ArgumentParser()
parser.add_argument('list_paths', nargs='+', default=[], help='paths to list files generated by parse_db.py')
parser.add_argument('-o', '--output', type=str, help='name of output file')
parser.add_argument('--analyze', action='store_true', help = 'print analysis and exit')

args = parser.parse_args()

###############################
####### setup input/output files
###############################

# # input file setup
# content = ""
# for path in args.list_paths :
# 	if os.path.splitext(args.path_to_db)[1] == ".gz" :
# 		file = gzip.open(args.path_to_db, "rt")
# 	elif os.path.splitext(args.path_to_db)[1] == ".bz2" :
# 		file = bz2.open(args.path_to_db, "rt")
# 	else :
# 		file = open(args.path_to_db, "r")
# 	content += file.read().strip() + '\n'
# 	file.close()

if args.analyze :
	analyze(args.list_paths)
	exit()

# output file setup
if args.output is None :
	if(len(args.list_paths) > 1) :
		print("Output name must be specified when multiple inputs are given")
		exit(1)
	args.output = os.path.splitext(args.list_paths[0])[0]
	if args.output[-9:] == ".pgn.list" :
		args.output = args.output[:-9] + ".chessz"
	elif args.output[-4:] == ".pgn" :
		args.output = args.output[:-4] + ".chessz"
	else :
		args.output += ".chessz"

out = open(args.output, "wb")

###############################
####### Compress
###############################

move_counts = analyze(args.list_paths)

# iterate in order of frequency
for (move, _) in move_counts.most_common() :
	out.write(header_move_to_bytes(move))

# pad the header to the expected size
assert len(move_counts) <= 1972
if(len(move_counts) < 1972) :
	out.write(bytearray((1972 - len(move_counts))*2))

# create fast searchable dictionary to convert move to index
move_index = {}
for i, (move, _) in enumerate(move_counts.most_common()) :
	move_index[move] = i + 1 # skip 0 so as not to be ambiguous with terminator - can have 0 as second byte since it won't be checked for terminator

# print([(i+1,move) for (i, (move, _)) in enumerate(move_counts.most_common())])

for path in args.list_paths :
	file = open_list(path)
	content = file.readlines()
	file.close()

	for i in range(0, len(content), 3) :
		end_reason = content[i].strip()
		winner = content[i+1].strip()
		moves = content[i+2].strip().split(' ')
		move_bytes = [index_to_bytes(move_index[move]) for move in moves]
		game_bytes = reason_to_byte(end_reason, winner)
		for b in move_bytes :
			game_bytes += b
		game_bytes += b'\x00' # terminator
		out.write(game_bytes)

out.close()