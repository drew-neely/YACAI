
import PySimpleGUI as sg
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import chess
import time

from yacai_agent import YACAI_Agent


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

def redraw_board(window, board):
	for sq in chess.SQUARES :
		piece = board.piece_at(sq)
		piece_str = piece.symbol() if piece else ''
		color = square_colors[sq]
		piece_image = images[piece_str]
		elem = window.FindElement(key=chess.square_name(sq))
		elem.Update(button_color=('white', color),
					image_filename=piece_image, )
	window.finalize()

def get_board_layout(board, white_perspective=True) :
	board_layout = [[None] * 8 for _ in range(8)]
	# file = column - rank = row
	for sq in chess.SQUARES :
		piece = board.piece_at(sq)
		piece_str = piece.symbol() if piece else ''
		row, col = (7 - chess.square_rank(sq), chess.square_file(sq))
		piece_image = images[piece_str]
		sq_button = sg.RButton('', image_filename=piece_image, size=(1, 1),
						border_width=0, button_color=('white', square_colors[sq]),
						pad=(0, 0), key=chess.square_name(sq))
		if white_perspective :
			board_layout[row][col] = sq_button
		else :
			board_layout[7-row][7-col] = sq_button
	return board_layout

def get_square_click(window) :
	event, _ = window.read()
	if event == sg.WIN_CLOSED :
		window.close()
		exit()
	else :
		return chess.parse_square(event)

class UserAgent() :
	def __init__(self, window) :
		self.window = window

	def highlight(self, board, sqs) :
		global square_colors
		for sq in sqs :
			square_colors[sq] = show_move_sq_light_color if is_square_light(sq) else show_move_sq_dark_color
		redraw_board(self.window, board)

	def get_promotion_piece(self, color):
		piece = None
		board_layout = []

		# Loop through board and create buttons with images        
		piece_symbols = ['N', 'B', 'R', 'Q'] if color == chess.WHITE else ['n', 'b', 'r', 'q']
		colors = [sq_dark_color, sq_light_color, sq_dark_color, sq_light_color]
		for piece_symbol in piece_symbols :
			piece_image = images[piece_symbol]
			square = sg.RButton('', image_filename=piece_image, size=(1, 1),
						border_width=0, button_color=('white', colors.pop()),
						pad=(0, 0), key=piece_symbol)
			board_layout.append(square)

		board_layout = [board_layout]

		promo_window = sg.Window('Select Promotion Type', board_layout,
								default_button_element_size=(12, 1),
								auto_size_buttons=False)

		piece, _ = promo_window.Read()
		if piece == sg.WIN_CLOSED :
			return self.get_promotion_piece(color)
		assert piece in piece_symbols
		promo_window.Close()
		return piece.lower()

	def get_move(self, board, color) :
		global square_colors
		moves = list(board.legal_moves)
		move_sqs = [(m.from_square, m.to_square) for m in moves]
		starting_sq_colors = {sq: c for sq,c in square_colors.items()}
		saved_from_sq = None
		while True :
			if saved_from_sq :
				from_sq = saved_from_sq
				saved_from_sq = None
			else :
				from_sq = get_square_click(self.window)
			piece = board.piece_at(from_sq)
			if piece == None or piece.color != color :
				redraw_board(self.window, board)
				continue
			dest_sqs = [sq2 for (sq1, sq2) in move_sqs if sq1 == from_sq]
			self.highlight(board, dest_sqs + [from_sq])
			if not dest_sqs : # piece cannot move
				square_colors = {sq: c for sq,c in starting_sq_colors.items()}
				continue
			to_sq = get_square_click(self.window)
			if to_sq in dest_sqs :
				move_str = chess.square_name(from_sq) + chess.square_name(to_sq)
				if piece.piece_type == chess.PAWN and chess.square_rank(to_sq) in [0,7] :
					move_str += self.get_promotion_piece(color)
				move = chess.Move.from_uci(move_str)
				assert move in moves
				return move
			else :
				piece = board.piece_at(to_sq)
				if piece != None and piece.color == color :
					saved_from_sq = to_sq
				square_colors = {sq: c for sq,c in starting_sq_colors.items()}
				redraw_board(self.window, board)
				continue


def start_game(white_agent, black_agent, board=None, perspective=chess.WHITE) :
	if board == None :
		board = chess.Board()
	
	layout = get_board_layout(board, perspective==chess.WHITE)
	window = sg.Window("Chess", layout)

	agents = [white_agent, black_agent]
	for i in [0, 1] :
		if isinstance(agents[i], str) :
			if agents[i].lower() == "user" :
				agents[i] = UserAgent(window)
			else :
				agents[i] = YACAI_Agent.from_file(ps)
	
	window.Finalize()

	whites_turn = board.turn == chess.WHITE
	while not board.is_game_over(claim_draw = True):
		move = None
		if whites_turn :
			move = agents[0].get_move(board, chess.WHITE)
		else :
			move = agents[1].get_move(board, chess.BLACK)
		board.push(move)
		reset_square_colors()
		for sq in [move.from_square, move.to_square] :
			square_colors[sq] = move_sq_light_color if is_square_light(sq) else move_sq_dark_color
		redraw_board(window, board)
		whites_turn = not whites_turn
		
	result = board.result()
	if result == "1-0" :
		print("WHITE WON!")
	elif result == "0-1" :
		print("BLACK WON!")
	else :
		print("DRAW!")

	window.close()


if __name__ == "__main__" :
	assert len(sys.argv) == 4, "Wrong number of arguments"
	assert sys.argv[3].lower() in ["white", "black"], "Invalid color of perspective"
	
	start_game(sys.argv[1], sys.argv[2], perspective = chess.WHITE if sys.argv[3].lower() == "white" else chess.BLACK)
	