
import chess
from math import inf

class Score :

	# cached score objects (like small java Integers)
	# initialized after class definition
	WHITE_CHECKMATE = None
	BLACK_CHECKMATE = None
	NUM_CACHED_MATE_IN = 16
	WHITE_MATE_IN = None
	BLACK_MATE_IN = None
	ZERO = None

	# types of scores
	T_NORMAL = 0
	T_CHECKMATE = 1
	T_MATE_IN = 2

	# if mate is False and val is finite         - val is the evaluation
	# if mate is False and val is infinite       - position is checkmate for white (val = +inf) or black (val = -inf)
	# if mate is True and val is finite non-zero - val is the number of moves to mate for white (val > 0) or black (val < 0)
	# if mate is True and val = 0                - Illegal state - undefined behavior
	# if mate is True and val is infinite        - Illegal state - undefined behavior
	#
	# this constructor should not be called from outside of this file - use the factory methods:
	# 	checkmate, mate_in, draw, score
	def __init__(self, val, mate = False) :
		assert not mate or (val != -inf and val != 0 and val != inf), f"Score initialized with an illegal state: <{self.val}, {self.mate}>"
		self.val = val
		self.is_mate = mate

		if not self.is_mate and self.val != -inf and self.val != inf :
			self.type = Score.T_NORMAL
		elif not self.is_mate and (self.val == -inf or self.val == inf) :
			self.type = Score.T_CHECKMATE
		elif self.is_mate and self.val != -inf and self.val != inf and self.val != 0 :
			self.type = Score.T_MATE_IN
		else :
			assert False, f"Internal Error - score initialized with invalid state: <{self.val}, {self.is_mate}>"

	# if self represents a mate in or checkmate, increases absolute value of half moves by 1
	# otherwise returns self unchanged
	def inc(self) :
		if self.type == Score.T_NORMAL :
			return self
		elif self.type == Score.T_MATE_IN :
			color = chess.WHITE if self.val > 0 else chess.BLACK
			return Score.mate_in(abs(self.val) + 1, color)
		elif self.type == Score.T_CHECKMATE :
			return Score.WHITE_MATE_IN[1] if self.val == inf else Score.BLACK_MATE_IN[1]
		else :
			assert False , f"Internal Error - bad type: {self.type}"

	@staticmethod
	def checkmate(color) :
		return Score.WHITE_CHECKMATE if color == chess.WHITE else Score.BLACK_CHECKMATE

	@staticmethod
	def mate_in(half_moves, color) :
		if half_moves < Score.NUM_CACHED_MATE_IN :
			cached_mates = Score.WHITE_MATE_IN if color == chess.WHITE else Score.BLACK_MATE_IN
			return cached_mates[half_moves]
		else :
			val = half_moves if color == chess.WHITE else -half_moves
			return Score(val, mate=True)
	
	@staticmethod
	def draw() :
		return Score.ZERO

	@staticmethod
	def score(val) :
		if val == 0 :
			return Score.ZERO
		else :
			return Score(val)
		
	def __eq__(self, other) :
		return self.val == other.val and self.is_mate == other.is_mate

	def __ne__(self, other) :
		return self.val != other.val or self.is_mate != other.is_mate

	def __lt__(self, other) :
		if not self.is_mate and not other.is_mate :
			return self.val < other.val
		if self.is_mate and other.is_mate :
			if (self.val < 0 and other.val < 0) or (self.val > 0 and other.val > 0) :
				return self.val > other.val
			else :
				return self.val < other.val
		elif self.is_mate :
			return (self.val < 0 or other.val == inf) and other.val != -inf
		else :
			return (other.val > 0 or self.val == -inf) and self.val != inf

	def __le__(self, other) :
		if not self.is_mate and not other.is_mate :
			return self.val <= other.val
		if self.is_mate and other.is_mate :
			if (self.val < 0 and other.val < 0) or (self.val > 0 and other.val > 0) :
				return self.val >= other.val
			else :
				return self.val <= other.val
		elif self.is_mate :
			return (self.val < 0 or other.val == inf) and other.val != -inf
		else :
			return (other.val > 0 or self.val == -inf) and self.val != inf

	def __gt__(self, other) :
		if not self.is_mate and not other.is_mate :
			return self.val > other.val
		if self.is_mate and other.is_mate :
			if (self.val < 0 and other.val < 0) or (self.val > 0 and other.val > 0) :
				return self.val < other.val
			else :
				return self.val > other.val
		elif self.is_mate :
			return (self.val > 0 or other.val == -inf) and other.val != inf
		else :
			return (other.val < 0 or self.val == inf) and self.val != -inf

	def __ge__(self, other) :
		if not self.is_mate and not other.is_mate :
			return self.val >= other.val
		if self.is_mate and other.is_mate :
			if (self.val < 0 and other.val < 0) or (self.val > 0 and other.val > 0) :
				return self.val <= other.val
			else :
				return self.val >= other.val
		elif self.is_mate :
			return (self.val > 0 or other.val == -inf) and other.val != inf
		else :
			return (other.val < 0 or self.val == inf) and self.val != -inf

	def __str__(self) :
		sign = ''
		if self.val > 0 :
			sign = '+'
		elif self.val < 0 :
			sign = '-'
		mate = 'M' if self.is_mate or self.val == -inf or self.val == inf else ''
		val_str = '0' if self.val == -inf or self.val == inf else str(abs(self.val))
		return f"{sign}{mate}{val_str}"

	def __repr__(self) :
		return str(self)

# initialize cached Score objects
Score.WHITE_CHECKMATE = Score(inf)
Score.BLACK_CHECKMATE = Score(-inf)
Score.WHITE_MATE_IN = {i: Score( i, mate=True) for i in range(1,Score.NUM_CACHED_MATE_IN)}
Score.BLACK_MATE_IN = {i: Score(-i, mate=True) for i in range(1,Score.NUM_CACHED_MATE_IN)}
Score.WHITE_MATE_IN[0] = Score.WHITE_CHECKMATE
Score.BLACK_MATE_IN[0] = Score.BLACK_CHECKMATE
Score.ZERO = Score(0)

if __name__ == "__main__" : 
	# run tests

	from itertools import product

	wcm = Score.mate_in(0, chess.WHITE)
	bcm = Score.mate_in(0, chess.BLACK)

	wmi = [Score.mate_in(i, chess.WHITE) for i in range(0, 100)]
	bmi = [Score.mate_in(i, chess.BLACK) for i in range(0, 100)]

	draw = Score.draw()

	w1 = Score.score(1)
	w2 = Score.score(2)
	wpi = Score.score(3.14)
	w10 = Score.score(10)

	b1 = Score.score(-1)
	b2 = Score.score(-2)
	bpi = Score.score(-3.14)
	b10 = Score.score(-10)

	scores = [bcm, bmi[1], bmi[10], bmi[99], b10, bpi, b2, b1, draw, w1, w2, wpi, w10, wmi[99], wmi[10], wmi[1], wcm]
	score_perms = [(a,b) for (a,b) in product(scores, repeat=2)]
	index_perms = list(product(range(len(scores)), repeat=2))
	
	eq_res = [a == b for (a,b) in index_perms]
	ne_res = [a != b for (a,b) in index_perms]
	lt_res = [a <  b for (a,b) in index_perms]
	le_res = [a <= b for (a,b) in index_perms]
	gt_res = [a >  b for (a,b) in index_perms]
	ge_res = [a >= b for (a,b) in index_perms]

	# print(list(zip(score_perms, eq_res)))

	for (a, b), res in zip(score_perms, eq_res) :
		assert (a == b) == res, f"Failed score test: {a} == {b} ==> {a==b}"

	for (a, b), res in zip(score_perms, ne_res) :
		assert (a != b) == res, f"Failed score test: {a} != {b} ==> {a!=b}"

	for (a, b), res in zip(score_perms, lt_res) :
		assert (a < b) == res, f"Failed score test: {a} < {b} ==> {a<b}"

	for (a, b), res in zip(score_perms, le_res) :
		assert (a <= b) == res, f"Failed score test: {a} <= {b} ==> {a<=b}"

	for (a, b), res in zip(score_perms, gt_res) :
		assert (a > b) == res, f"Failed score test: {a} > {b} ==> {a>b}"

	for (a, b), res in zip(score_perms, ge_res) :
		assert (a >= b) == res, f"Failed score test: {a} >= {b} ==> {a>=b}"

	for i in range(len(wmi) - 1) :
		assert wmi[i].inc() == wmi[i+1], f"Failed score test: ({wmi[i]}).inc() ==> {wmi[i].inc()}"

	for i in range(len(bmi) - 1) :
		assert bmi[i].inc() == bmi[i+1], f"Failed score test: ({wmi[i]}).inc() ==> {wmi[i].inc()}"

	for a in [w1, w2, wpi, w10, draw, b1, b2, bpi, b10] :
		assert a.inc() == a, f"Failed score test: ({a}).inc() ==> {a.inc()}"

	print("passed all tests\n")

	



	
	
