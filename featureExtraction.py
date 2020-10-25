import chess

from feature import Feature

class PointDifference(Feature) :
	
	piece_values = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3, chess.ROOK: 5, chess.QUEEN: 9}

	# determines the difference in the value of the pieces of the two players.
	# game is a chess board from the chess library.
	# player_color is one of chess.WHITE or chess.BLACK.
	def extract(self, game, player_color) :
		pieces = []
		total = 0
		for sq in chess.SQUARES :
			p = game.piece_at(sq)
			if p != None and p.piece_type != chess.KING and p.color == player_color:
				total += self.piece_values[p]
			if p != None and p.piece_type != chess.KING and p.color != player_color:
				total -= self.piece_values[p]
		
		return total
class simpleFeatures(Feature) :
	piece_values = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3, chess.ROOK: 5, chess.QUEEN: 9}

	def extract(self, game, player_color) :
		pieces = []
		pieceTotal = 0
		valueK = valueB = valueR = 0
		queenDiff = 0
		for sq in chess.SQUARES :
			p = game.piece_at(sq)
			if p != None and p.piece_type != chess.KING and p.color == player_color:
				pieceTotal += self.piece_values[p]
			if p != None and p.piece_type != chess.KING and p.color != player_color:
				pieceTotal -= self.piece_values[p]
			if p.piece_type == chess.KNIGHT and player_color == p.color:
				valueK += 1
			elif p.piece_type == chess.KNIGHT and player_color != p.color:
				valueK -= 1
			elif p.piece_type == chess.BISHOP and player_color == p.color:
				valueB += 1
			elif p.piece_type == chess.BISHOP and player_color != p.color:
				valueK -= 1
			elif p.piece_type == chess.ROOK and player_color == p.color:
				valueR += 1
			elif p.piece_type == chess.ROOK and player_color -= p.color:
				valueR -= 1
			if p.piece_type == chess.QUEEN and player_color == p.color:
				queenDiff += 1
			if p.piece_type == chess.QUEEN and player_color != p.color:
				queenDiff -= 1

		
		return [pieceTotal, valueK, valueB, valueR, queenDiff]

class TwoOfAKind(Feature) :		

	# two of a kind means having 2 knights or 2 bishops.
	# adds the number of two of a kind of a knight, bishop, or rook, and subtracts from how many 
	# two of a kind the opponent has.

	def extract(self, game, player_color) :

		valueK = valueB = valueR = valueK2 = valueB2 = valueR2 = 0

		for sq in chess.SQUARES: 
			p = game.piece_at(sq)
			if p.piece_type == chess.KNIGHT and player_color == p.color:
				valueK += 1
			elif p.piece_type == chess.KNIGHT and player_color != p.color:
				valueK2 -= 1
			if p.piece_type == chess.BISHOP and player_color == p.color:
				valueB += 1
			elif p.piece_type == chess.BISHOP and player_color != p.color:
				valueB2 -= 1
			if p.piece_type == chess.ROOK and player_color == p.color:
				valueR += 1
			elif p.piece_type == chess.ROOK and player_color != p.color:
				valueR2 -= 1

		Kpair = valueK//2 + math.ceil(valueK2/2)
		Bpair = valueB//2 + math.ceil(valueB2/2)
		Rpair = valueR//2 + math.ceil(valueR2/2)
			
		return [Kpair, Bpair, Rpair]








class Checkmated(Feature) :

	# Are you in checkmate? Courtesy of Drew.

	def extract(self, game, player_color) :

		for col in chess.Color:
			if player_color == col and game.is_checkmate() == True:
				value = 1
			elif player_color != col and game.is_checkmate() == True:
				value = -1
			else:
				value = 0

			return value

#class HaveQueen(Feature) :		

	# difference in the number of queens the players have

#	def extract(self, game, player_color) :

#		value = 0
#		for sq in chess.SQUARES: 
#			p = game.piece_at(sq)
#			if p.piece_type == chess.QUEEN and player_color == p.color:
#				value += 1
#			if p.piece_type == chess.QUEEN and player_color != p.color:
#				value -= 1
		# for sq in chess.SQUARES: 
		# 	p = p.piece_type
		# 	if p.piece_type == chess.QUEEN and player_color != p.color:
		# 		value -= 1

#		return value