from ctypes import *
import ctypes.util
import pathlib
from chess import Move

chess = CDLL(pathlib.Path().absolute() / "bin" / "cpp-chess")

libc_name = ctypes.util.find_library("c")
if libc_name is None:
	raise OSError("Unable to locate the C standard library")
libc = CDLL(libc_name)

# libc free(void* p) => void
# free = libc.free
# free.argtypes = [c_void_p]

# create_board() => int
create_board = chess.create_board
create_board.res_type = c_int
create_board.argtypes = []

# create_board_from_fen(const char* fen) => int
create_board_from_fen = chess.create_board_from_fen
create_board_from_fen.res_type = c_int
create_board_from_fen.argtypes = [c_char_p]

# free_board(int bd) => void
free_board = chess.free_board
free_board.res_type = None
free_board.argtypes = [c_int]

# make_move(int bd, const char* uci_move) => void
make_move = chess.make_move
make_move.res_type = None
make_move.argtypes = [c_int, c_char_p]

# unmake_move(int bd) => void
unmake_move = chess.unmake_move
unmake_move.res_type = None
unmake_move.argtypes = [c_int]

# countPositions(uint8_t depth) => uint64_t
count_positions = chess.count_positions
count_positions.restype = c_ulonglong
count_positions.argtypes = [c_int, c_ubyte]

# get_fen(int bd) => char*
get_fen = chess.get_fen
get_fen.restype = c_void_p # really returns a c_char_p, but can only be freed if a raw pointer is returned
get_fen.argtypes = [c_int]

class Board() :

	def __init__(self, fen=None) :
		if fen == None :
			self.bd = create_board()
		else :
			self.bd = create_board_from_fen(fen.encode('utf-8'))
		if self.bd < 0 : # Couldnt make new board
			print(self.bd)
			raise MemoryError("Couldn't allocate board")
	
	def make_move(self, move) :
		uci = move.uci().encode('ascii')
		make_move(self.bd, uci)
	
	def unmake_move(self) :
		unmake_move(self.bd)

	def count_positions(self, depth) :
		return count_positions(self.bd, depth)

	def get_fen(self) :
		_fen = get_fen(self.bd)
		if not _fen :
			raise MemoryError("Failed to allocate FEN string")
		try :
			result = cast(_fen, c_char_p).value.decode("utf-8")
		finally :
			libc.free(_fen)
		return result


	def free(self) : 
		# C++ memory needs to be freed when the board is garbage collected
		free_board(self.bd)

	
	
