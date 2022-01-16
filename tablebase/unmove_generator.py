import chess

""" 
The functions in this file are set as a property on chess.Board 
	(ie. it becomes a class method and basically extends the 
	library functionality). Thus, they takes a self parameter which
	is a board
"""

# pseudo_legal_moves returns a dynamic array/iterator that throws away results 
# 	upon turn changing, so convert to list befor changing turn back
# TODO : This method will need to exist in multiple forms to work with different
# 	engame piece compositions.
def unmoves(self) :
	self.turn = not self.turn
	assert not self.is_check()
	moves = list(self.pseudo_legal_moves)
	moves = [m for m in moves if not self.gives_check(m)] # cannot have previous position with king in check
	moves = [m for m in moves if not self.is_capture(m)] # cannot have captures in backwards moves position with king in check
	for m in moves :
		(m.from_square, m.to_square) = (m.to_square, m.from_square) # switch direction of move
	self.turn = not self.turn
	return moves

# pushes a move that represents an unmove (ie. undoes the move)
def unpush(self, move) :
	piece = self.remove_piece_at(move.to_square)
	assert piece != None
	self.set_piece_at(move.from_square, piece)
	self.turn = not self.turn

# pops a move that represents an unmove (ie. does the move)
def unpop(self, move) :
	piece = self.remove_piece_at(move.from_square)
	assert piece != None
	self.set_piece_at(move.to_square, piece)
	self.turn = not self.turn

# called with 'board.unmoves' (properties don't use '()')
chess.Board.unmoves = property(unmoves)
chess.Board.unpush = unpush
chess.Board.unpop = unpop