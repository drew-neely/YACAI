
import os
import sys
import tkinter as tk

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import chess

# from yacai_agent import YACAI_Agent


BLANK = 0  # piece names
PAWNB = 1
KNIGHTB = 2
BISHOPB = 3
ROOKB = 4
KINGB = 5
QUEENB = 6
PAWNW = 7
KNIGHTW = 8
BISHOPW = 9
ROOKW = 10
KINGW = 11
QUEENW = 12

IMAGE_PATH = os.path.join(os.path.dirname(__file__), "Images")  # path to the chess pieces

blank = os.path.join(IMAGE_PATH, 'blank.png')
bishopB = os.path.join(IMAGE_PATH, 'bB.png')
bishopW = os.path.join(IMAGE_PATH, 'wB.png')
pawnB = os.path.join(IMAGE_PATH, 'bP.png')
pawnW = os.path.join(IMAGE_PATH, 'wP.png')
knightB = os.path.join(IMAGE_PATH, 'bN.png')
knightW = os.path.join(IMAGE_PATH, 'wN.png')
rookB = os.path.join(IMAGE_PATH, 'bR.png')
rookW = os.path.join(IMAGE_PATH, 'wR.png')
queenB = os.path.join(IMAGE_PATH, 'bQ.png')
queenW = os.path.join(IMAGE_PATH, 'wQ.png')
kingB = os.path.join(IMAGE_PATH, 'bK.png')
kingW = os.path.join(IMAGE_PATH, 'wK.png')


images = {'b': bishopB, 'B': bishopW, 'p': pawnB, 'P': pawnW,
          'n': knightB, 'N': knightW,
          'r': rookB, 'R': rookW, 'k': kingB, 'K': kingW,
          'q': queenB, 'Q': queenW, '': blank}

sq_light_color = '#F0D9B5'
sq_dark_color = '#B58863'

move_sq_light_color = '#E8E18E'
move_sq_dark_color = '#B8AF4E'

show_move_sq_light_color = '#99C7DF'
show_move_sq_dark_color = '#4293BC'

def is_square_light(sq) :
	row, col = (7 - chess.square_rank(sq), chess.square_file(sq))
	return (row + col) % 2 == 0

square_colors = {}

def reset_square_colors() :
	global square_colors
	square_colors = {sq: sq_light_color if is_square_light(sq) else sq_dark_color for sq in chess.SQUARES}

reset_square_colors()

class ChessGUI:
	def __init__(self, board, white_perspective=True):
		self.white_perspective = white_perspective
		self.root = tk.Tk()
		self.root.title("Chess")
		self.root.protocol("WM_DELETE_WINDOW", self._on_close)
		self._closed = False

		self.selected_square = tk.StringVar()
		self.board_frame = tk.Frame(self.root)
		self.board_frame.pack(padx=0, pady=0)

		self.piece_images = self._load_images()
		self.square_buttons = {}
		self._build_board(board)
		self.redraw_board(board)

	def _load_images(self):
		loaded = {}
		for key, path in images.items():
			loaded[key] = tk.PhotoImage(file=path)
		return loaded

	def _build_board(self, board):
		for sq in chess.SQUARES:
			row, col = 7 - chess.square_rank(sq), chess.square_file(sq)
			display_row, display_col = self._transform_coordinates(row, col)
			square_name = chess.square_name(sq)
			button = tk.Button(
				self.board_frame,
				image=self.piece_images[''],
				borderwidth=0,
				relief="flat",
				background=square_colors[sq],
				activebackground=square_colors[sq],
				command=lambda name=square_name: self._on_square_click(name),
			)
			button.grid(row=display_row, column=display_col, padx=0, pady=0, ipadx=0, ipady=0)
			self.square_buttons[square_name] = button

	def _transform_coordinates(self, row, col):
		if self.white_perspective:
			return row, col
		return 7 - row, 7 - col

	def _on_square_click(self, square_name):
		self.selected_square.set(square_name)

	def _on_close(self):
		self._closed = True
		self.selected_square.set("WINDOW_CLOSED")

	def redraw_board(self, board):
		for sq in chess.SQUARES:
			piece = board.piece_at(sq)
			piece_symbol = piece.symbol() if piece else ''
			color = square_colors[sq]
			square_name = chess.square_name(sq)
			button = self.square_buttons[square_name]
			button.configure(
				image=self.piece_images[piece_symbol],
				background=color,
				activebackground=color,
			)
		self.root.update_idletasks()

	def wait_for_square(self):
		self.selected_square.set("")
		while True:
			self.root.wait_variable(self.selected_square)
			value = self.selected_square.get()
			if value == "WINDOW_CLOSED":
				self.close()
				sys.exit(0)
			if value:
				return chess.parse_square(value)

	def show_promotion_dialog(self, color):
		piece_symbols = ['N', 'B', 'R', 'Q'] if color == chess.WHITE else ['n', 'b', 'r', 'q']
		colors = [sq_dark_color, sq_light_color, sq_dark_color, sq_light_color]
		selected_piece = tk.StringVar()

		dialog = tk.Toplevel(self.root)
		dialog.title("Select Promotion Type")
		dialog.grab_set()
		dialog.protocol("WM_DELETE_WINDOW", lambda: selected_piece.set(""))

		for idx, piece_symbol in enumerate(piece_symbols):
			piece_image = self.piece_images[piece_symbol]
			bg_color = colors[idx]
			button = tk.Button(
				dialog,
				image=piece_image,
				borderwidth=0,
				relief="flat",
				background=bg_color,
				activebackground=bg_color,
				command=lambda sym=piece_symbol: selected_piece.set(sym),
			)
			button.grid(row=0, column=idx, padx=0, pady=0, ipadx=0, ipady=0)

		dialog.wait_variable(selected_piece)
		dialog.grab_release()
		dialog.destroy()

		choice = selected_piece.get()
		if not choice:
			return self.show_promotion_dialog(color)
		return choice.lower()

	def close(self):
		if not self._closed:
			self._closed = True
			self.root.destroy()


class UserAgent:
	def __init__(self, gui):
		self.gui = gui

	def highlight(self, board, squares):
		global square_colors
		for sq in squares:
			square_colors[sq] = show_move_sq_light_color if is_square_light(sq) else show_move_sq_dark_color
		self.gui.redraw_board(board)

	def get_promotion_piece(self, color):
		return self.gui.show_promotion_dialog(color)

	def get_move(self, board, color):
		global square_colors
		moves = list(board.legal_moves)
		move_sqs = [(m.from_square, m.to_square) for m in moves]
		starting_sq_colors = {sq: c for sq, c in square_colors.items()}
		saved_from_sq = None

		while True:
			if saved_from_sq is not None:
				from_sq = saved_from_sq
				saved_from_sq = None
			else:
				from_sq = self.gui.wait_for_square()

			piece = board.piece_at(from_sq)
			if piece is None or piece.color != color:
				square_colors = {sq: c for sq, c in starting_sq_colors.items()}
				self.gui.redraw_board(board)
				continue

			dest_sqs = [sq2 for (sq1, sq2) in move_sqs if sq1 == from_sq]
			self.highlight(board, dest_sqs + [from_sq])

			if not dest_sqs:
				square_colors = {sq: c for sq, c in starting_sq_colors.items()}
				continue

			to_sq = self.gui.wait_for_square()
			if to_sq in dest_sqs:
				move_str = chess.square_name(from_sq) + chess.square_name(to_sq)
				if piece.piece_type == chess.PAWN and chess.square_rank(to_sq) in [0, 7]:
					move_str += self.get_promotion_piece(color)
				move = chess.Move.from_uci(move_str)
				assert move in moves
				return move
			else:
				piece = board.piece_at(to_sq)
				if piece is not None and piece.color == color:
					saved_from_sq = to_sq
				square_colors = {sq: c for sq, c in starting_sq_colors.items()}
				self.gui.redraw_board(board)
				continue


def start_game(white_agent, black_agent, board=None, perspective=chess.WHITE):
	if board is None:
		board = chess.Board()

	gui = ChessGUI(board, white_perspective=(perspective == chess.WHITE))

	agents = [white_agent, black_agent]
	for i in [0, 1]:
		if isinstance(agents[i], str):
			if agents[i].lower() == "user":
				agents[i] = UserAgent(gui)
			else:
				raise Exception("YACAI_Agent not found")
				# agents[i] = YACAI_Agent.from_file(agents[i])

	whites_turn = board.turn == chess.WHITE
	while not board.is_game_over(claim_draw=True):
		if whites_turn:
			move = agents[0].get_move(board, chess.WHITE)
		else:
			move = agents[1].get_move(board, chess.BLACK)
		board.push(move)
		reset_square_colors()
		for sq in [move.from_square, move.to_square]:
			square_colors[sq] = move_sq_light_color if is_square_light(sq) else move_sq_dark_color
		gui.redraw_board(board)
		whites_turn = not whites_turn

	result = board.result()
	if result == "1-0":
		print("WHITE WON!")
	elif result == "0-1":
		print("BLACK WON!")
	else:
		print("DRAW!")

	gui.close()


if __name__ == "__main__" :
	assert len(sys.argv) == 4, "Wrong number of arguments"
	assert sys.argv[3].lower() in ["white", "black"], "Invalid color of perspective"
	
	start_game(sys.argv[1], sys.argv[2], perspective = chess.WHITE if sys.argv[3].lower() == "white" else chess.BLACK)
	
