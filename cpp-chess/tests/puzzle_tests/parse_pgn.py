
import os
import re
import chess, chess.pgn

input_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "puzzle_pgns"))
output_filename = os.path.abspath(os.path.join(os.path.dirname(__file__), "puzzles.list"))
print(output_filename)
filenames = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if re.fullmatch(r"puzzle_\d+\.pgn", f)]
filenames.sort()
print(f"Identified {len(filenames)} puzzle pgn files")


with open(output_filename, "w") as out :
    for filename in filenames :
        with open(filename) as pgn :
            game = chess.pgn.read_game(pgn)
            fen = game.headers["FEN"]
            moves = ' '.join([move.uci() for move in game.mainline_moves()])

            out.write(fen + "\n")
            out.write(moves + "\n")
            
    

