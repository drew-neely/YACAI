import chess

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

base_square_values = [
	 0,  1,  2,  3, 16, 17, 18, 19,
	10,  4,  5,  6, 20, 21, 22, 23,
	11, 12,  7,  8, 24, 25, 26, 27,
	13, 14, 15,  9, 28, 29, 30, 31,
	32, 33, 34, 35, 36, 37, 38, 39,
	40, 41, 42, 43, 44, 45, 46, 47,
	48, 49, 50, 51, 52, 53, 54, 55,
	56, 57, 58, 59, 60, 61, 62, 63,
]

square_value_matrixs = [
	base_square_values,
	flipv(base_square_values),
	fliph(base_square_values),
	flipv(fliph(base_square_values)),
	fliph(rotc(base_square_values)),
	flipv(fliph(rotc(base_square_values))),
	rotc(base_square_values),
	flipv(rotc(base_square_values)),
]

matrix_index_wking_no_pawns = [
	0, 0, 0, 0, 1, 1, 1, 1,
	4, 0, 0, 0, 1, 1, 1, 5,
	4, 4, 0, 0, 1, 1, 5, 5,
	4, 4, 4, 0, 1, 5, 5, 5,
	6, 6, 6, 2, 3, 7, 7, 7,
	6, 6, 2, 2, 3, 3, 7, 7,
	6, 2, 2, 2, 3, 3, 3, 7,
	2, 2, 2, 2, 3, 3, 3, 3,
]

matrix_index_wking_pawns = [
	0, 0, 0, 0, 1, 1, 1, 1,
	0, 0, 0, 0, 1, 1, 1, 1,
	0, 0, 0, 0, 1, 1, 1, 1,
	0, 0, 0, 0, 1, 1, 1, 1,
	2, 2, 2, 2, 3, 3, 3, 3,
	2, 2, 2, 2, 3, 3, 3, 3,
	2, 2, 2, 2, 3, 3, 3, 3,
	2, 2, 2, 2, 3, 3, 3, 3,
]

def get_value_matrix(board, includes_pawns=False) :
	king = board.king(chess.WHITE)
	if not includes_pawns :
		index = matrix_index_wking_no_pawns[king]
	else :
		index = matrix_index_wking_pawns[king]
	return square_value_matrixs[index]
