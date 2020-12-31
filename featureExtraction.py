import chess
import math

from feature import Feature

class PointDifference(Feature) :
	
	piece_values = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3, chess.ROOK: 5, chess.QUEEN: 9}

	# determines the difference in the value of the pieces of the two players.
	# game is a chess board from the chess library.
	# player_color is one of chess.WHITE or chess.BLACK.
	def _extract(self, game, player_color) :
		pieces = []
		total = 0
		for sq in chess.SQUARES :
			p = game.piece_at(sq)
			if p != None and p.piece_type != chess.KING and p.color == player_color:
				total += self.piece_values[p.piece_type]
			if p != None and p.piece_type != chess.KING and p.color != player_color:
				total -= self.piece_values[p.piece_type]
		
		return [total]
		
class simpleFeatures(Feature) :
	piece_values = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3, chess.ROOK: 5, chess.QUEEN: 9}

	def _extract(self, game, player_color) :
		pieces = []
		pieceTotal = 0
		valueK = valueB = valueR = 0
		queenDiff = 0
		for sq in chess.SQUARES :
			p = game.piece_at(sq)
			if p != None :
				if p.piece_type != chess.KING and p.color == player_color:
					pieceTotal += self.piece_values[p.piece_type]
				if p.piece_type != chess.KING and p.color != player_color:
					pieceTotal -= self.piece_values[p.piece_type]
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
				elif p.piece_type == chess.ROOK and player_color != p.color:
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

	def _extract(self, game, player_color) :

		valueK = valueB = valueR = valueK2 = valueB2 = valueR2 = 0

		for sq in chess.SQUARES: 
			p = game.piece_at(sq)
			if p != None :
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

class CheckCheckmate(Feature) :

	# Are you in checkmate? Courtesy of Drew.

	def _extract(self, game, player_color) :
		checkmate = 1 if game.is_checkmate() else 0
		check = 1 if game.is_check() else 0
		
		opens_check = 0
		for move in game.legal_moves :
			if game.gives_check(move) :
				opens_check += 1

		return [checkmate, check, opens_check]
			

class PawnDistance(Feature) :	

	def _extract(self, game, player_color) :

		value = 0

		for sq in chess.SQUARES:
			p = game.piece_at(sq)

			if p != None and p.piece_type == chess.PAWN and player_color == chess.WHITE:
				value += abs(chess.square_rank(sq)-1)
			elif p != None and p.piece_type == chess.PAWN and player_color != chess.BLACK:
				value -= abs(chess.square_rank(sq)-6)

		return [value]

class AvgDisFromKing(Feature) :	

	def _extract(self, game, player_color) :
		
		myKingDisMyColor = myKingDisNotMyColor = NotMyKingDisMyColor = NotMyKingDisNotMyColor = 0
		NumOfMyColor = NumOfNotMyColor = 1
		for sq in chess.SQUARES:
			p = game.piece_at(sq)

			if p != None :
				if player_color == p.color and p.piece_type != chess.KING:
					myKingDisMyColor += chess.square_distance(sq,game.king(player_color))
				if player_color != p.color and p.piece_type != chess.KING:
					myKingDisNotMyColor += chess.square_distance(sq,game.king(player_color))
				if player_color == p.color and p.piece_type != chess.KING:
					NotMyKingDisMyColor += chess.square_distance(sq,game.king(not player_color))
				if player_color != p.color and p.piece_type != chess.KING:
					NotMyKingDisNotMyColor += chess.square_distance(sq,game.king(not player_color))
				if player_color == p.color and p.piece_type != chess.KING:
					NumOfMyColor += 1
				if player_color != p.color and p.piece_type != chess.KING:
					NumOfNotMyColor += 1

		myProduct = game.fullmove_number*(NumOfMyColor)**2
		otherProduct = game.fullmove_number*(NumOfNotMyColor)**2

		return [myKingDisMyColor/NumOfMyColor , myKingDisNotMyColor/NumOfNotMyColor , NotMyKingDisMyColor/NumOfMyColor , 
		NotMyKingDisNotMyColor/NumOfNotMyColor, 16 - NumOfMyColor , 16 - NumOfNotMyColor , myProduct , otherProduct]

class UnitDisFromKing(Feature) :	

	def _extract(self, game, player_color) : 
		valMyColor = valNotMyColor = 0

		for sq in chess.SQUARES:
			p = game.piece_at(sq)
			
			if p != None and player_color == p.color and chess.square_distance(sq,game.king(player_color)) == 1:
				valMyColor += 1
			if p != None and player_color != p.color and chess.square_distance(sq,game.king(not player_color)) == 1:
				valNotMyColor += 1
		
		return [valMyColor, valNotMyColor]

class NumOfLegalMoves(Feature) :	

	def _extract(self, game, player_color) : 

		board = chess.Board()
		return [board.legal_moves.count()]

class NumAttackDefendMoves(Feature) :	

	piece_values = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3, chess.ROOK: 5, chess.QUEEN: 9, chess.KING: 0}

	def _extract(self, game, player_color) : 

		myAttackNum = otherAttackNum = 0
		myDefendNum = otherDefendNum = 0
		myAttackNumP = otherAttackNumP = 0
		myDefendNumP = otherDefendNumP = 0
		middleAttacks = middlePieces = 0

		middle = ["d4", "d5", "e4", "e5", "c4", "c5", "f4", "f5"]

		for sq in chess.SQUARES:
			p = game.piece_at(sq)
			if p != None :
				sqs = game.attacks(sq)
				for sq2 in sqs :
					p2 = game.piece_at(sq2)
					if p2 != None :
						if player_color == p.color and player_color != p2.color:
							myAttackNum += 1
							myAttackNumP += self.piece_values[p2.piece_type]
						elif player_color != p.color and player_color == p2.color:
							otherAttackNum += 1
							otherAttackNumP += self.piece_values[p2.piece_type]
						elif player_color == p.color and player_color == p2.color:
							myDefendNum += 1
							myDefendNumP += self.piece_values[p2.piece_type]
						elif player_color != p.color and player_color != p2.color:
							otherDefendNum += 1
							otherDefendNumP += self.piece_values[p2.piece_type]
					if p.color == player_color and chess.square_name(sq2) in middle :
						middleAttacks += 1
				if p.color == player_color and chess.square_name(sq) in middle :
					middlePieces += 1

					
		return [myAttackNum, otherAttackNum, myDefendNum, otherDefendNum, 
					myAttackNumP, otherAttackNumP, myDefendNumP, otherDefendNumP,
					middleAttacks, middlePieces]
