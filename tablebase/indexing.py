import chess
from bisect import bisect

def printmat(mat) :
	for rank in reversed(range(8)) :
		print(',\t'.join([str(v) for v in mat[rank*8: rank*8+8]]) + ',')

# flip about the horizontal axis
def fliph(mat) :
	newmat = [-1] * 64
	for i in range(64) :
		newmat[i] = mat[(7-int(i/8))*8 + (i%8)]
	return newmat

# flip about the vertical axis
def flipv(mat) :
	newmat = [-1] * 64
	for i in range(64) :
		newmat[i] = mat[int(i/8) * 8 + (7-i%8)]
	return newmat

# rotate counterclockwise
def rotc(mat) :
	newmat = [-1] * 64
	for i in range(64) :
		newmat[i] = mat[(i%8)*8 + 7-(int(i/8))]
	return newmat

# given i = square position from python chess:
# base_square_index_np[i] = the transformed index for 
# 		square i to be used in table base indexing functions
base_square_index_np = [
	 0,  4,  5,  6, 10, 11, 12, 13,
	36,  1,  7,  8, 14, 15, 16, 17,
	37, 38,  2,  9, 18, 19, 20, 21,
	39, 40, 41,  3, 22, 23, 24, 25,
	42, 43, 44, 45, 26, 27, 28, 29,
	46, 47, 48, 49, 50, 30, 31, 32,
	51, 52, 53, 54, 55, 56, 33, 34,
	57, 58, 59, 60, 61, 62, 63, 35,
]

# All 8 possible roations of base_square_index_np
square_index_rots_np = [                       #  _______________
	base_square_index_np,                      # |\      |      /|
	flipv(base_square_index_np),               # |  \  2 | 3  /  |
	fliph(base_square_index_np),               # | 6  \  |  /   7|
	flipv(fliph(base_square_index_np)),        # |_____ \|/______|
	fliph(rotc(base_square_index_np)),         # |      /|\      |
	flipv(fliph(rotc(base_square_index_np))),  # | 4  /  |  \  5 |
	rotc(base_square_index_np),                # |  /  0 | 1  \  |
	flipv(rotc(base_square_index_np)),         # |/______|______\|
]

# given i = square position of white king:
# rot_index_np[i] = the index to use in square_index_rots_np
# 	to get the properly rotated matrix placing the white king on a square [0,9]
# When the king is on a diagonal two possible rotations exist with indecies :
# 	rot_index_np[i] and (rot_index_np[i] + 4) % i
# 	In this case the correct rotation to use is the one that puts the black king on
# 	a square with index [0,35]
rot_index_np = [
	0, 0, 0, 0, 1, 1, 1, 1,
	4, 0, 0, 0, 1, 1, 1, 5,
	4, 4, 0, 0, 1, 1, 5, 5,
	4, 4, 4, 0, 1, 5, 5, 5,
	6, 6, 6, 2, 3, 7, 7, 7,
	6, 6, 2, 2, 3, 3, 7, 7,
	6, 2, 2, 2, 3, 3, 3, 7,
	2, 2, 2, 2, 3, 3, 3, 3,
]

# given i = square position of white king:
# square_index_rots_bk_skips_np[i] lists the indecies at which the black king may not
# 	be legaly placed (kings may not be next to or on top of each other)
# the index of the black king among the legal squares can be calculated as 
# 	bk' = bk - bisect(square_index_rots_bk_skips_np[i], bk)
# 	where bk is the translated square position of th blaack king
square_index_rots_bk_skips_np = [
	[0, 1, 4],                         # 0
	[0, 1, 2, 4, 5, 7],                # 1
	[1, 2, 3, 7, 8, 9],                # 2
	[2, 3, 9, 18, 22, 26],             # 3
	[0, 1, 4, 5, 7, 36],               # 4
	[1, 4, 5, 6, 7, 8],                # 5
	[5, 6, 7, 8, 10, 14],              # 6
	[1, 2, 4, 5, 6, 7, 8, 9, 38],      # 7
	[2, 5, 6, 7, 8, 9, 10, 14, 18],    # 8
	[2, 3, 9, 18, 22, 26, 41, 44, 45], # 9
]


# calculate king_index with equation 
# 	base_from_wk_index[wk] + bk
base_from_wk_index = [0, 33, 63, 93, 123, 181, 239, 297, 352, 407]

# def get_value_matrix(board, includes_pawns=False) :
# 	king = board.king(chess.WHITE)
# 	if not includes_pawns :
# 		index = matrix_index_wking_no_pawns[king]
# 	else :
# 		index = matrix_index_wking_pawns[king]
# 	return square_value_matrixs[index]

def get_kings_index_np(board) :
	wk, bk = board.king(chess.WHITE), board.king(chess.BLACK)
	if wk is None or bk is None :
		raise ValueError("Missing a king")
	rot_index = rot_index_np[wk]
	square_index_mat = square_index_rots_np[rot_index]
	if square_index_mat[wk] < 4 and square_index_mat[bk] > 35 : 
		# white king is on diagonal and should be diagonally flipped to put black king on smaller index
		rot_index = (rot_index + 4) % 8
		square_index_mat = square_index_rots_np[rot_index]
	wk = square_index_mat[wk]
	bk = square_index_mat[bk]
	skip = bisect(square_index_rots_bk_skips_np[wk], bk)
	if square_index_rots_bk_skips_np[wk][skip-1] == bk : # black king is on invalid square
		raise ValueError("Kings placed on invalid squares")
	bk -= skip
	index = base_from_wk_index[wk] + bk
	return (index, square_index_mat)


# if __name__ == "__main__" :
# 	boards = [chess.Board("8/8/8/8/8/8/8/8 w - - 0 1") for _ in range(64 ** 2)]

# 	for i in range(64 ** 2) :
# 		wk = int(i / 64)
# 		bk = i % 64
# 		boards[i].set_piece_at(wk, chess.Piece(chess.KING, chess.WHITE))
# 		boards[i].set_piece_at(bk, chess.Piece(chess.KING, chess.BLACK))

# 	results = [None] * (64 ** 2)
# 	for i in range(64 ** 2) :
# 		try :
# 			results[i], _ = get_kings_index_np(boards[i])
# 		except ValueError as e:
# 			# print(e)
# 			pass
# 	print(len(results))
# 	results = [r for r in results if r is not None]
# 	print(len(results))
# 	results = set(results)
# 	print(len(results))
# 	print(min(results), max(results))


	
		
