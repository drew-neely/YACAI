import argparse
from timer import Timer
from big_array import BigArray
import chess
import unmove_generator # add unmove functions to chess.Board
from tablebase import Tablebase
from KQk import KQk

endgame_classes = {'KQk': KQk}

parser = argparse.ArgumentParser(description='YACAI Table Base Generator')
for type in endgame_classes.keys() :
	parser.add_argument(f'-{type}', dest='targets', action='append_const', const=type)
args = parser.parse_args()


if __name__ == "__main__" : 
	for target in args.targets :
		tb = endgame_classes[target]()
		if not tb.writable :
			print(f"WARNING: tablebase for {target} already exists - Nothing will be done")
			continue
		tb.build()
		# mates = tb.checkmate_positions()
		# print(f"number of mate positions: {len(mates)}")
		# print(sorted(list(mates.keys())))
		# for (m, b) in mates.items() :
		# 	print(m)
		# 	print(b)
		# 	print()
			
		# 	break
		tb.flush()

