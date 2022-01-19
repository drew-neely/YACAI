import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from math import inf
import chess

from minimax import Minimax
from score import Score


class ArrMinimax(Minimax) :
	def __init__(self, test_case, pruning=True, verbose=False):
		self.test_case = test_case
		self.stack = [test_case.arr]
		super().__init__(test_case.depth, maxing = test_case.maxing, pruning=pruning, verbose=verbose)

	def children(self) :
		return self.stack[-1]

	def eval(self) :
		assert isinstance(self.stack[-1], (int, float)), "Attempting to evaluate non-leaf in ArrMinimax.eval()"
		return self.stack[-1]

	def apply(self, choice) :
		self.stack.append(choice)

	def unapply(self) :
		self.stack.pop()

	@property
	def min_eval(self) :
		return -inf

	@property
	def max_eval(self) :
		return inf

	def inc_eval(self, e) :
		return e

	def __str__(self) :
		return str(self.stack[-1])

class TupMinimax(Minimax) :
	def __init__(self, test_case, use_score = False, pruning=True, verbose=False):
		self.test_case = test_case
		self.stack = [test_case.tup]
		self.use_score = use_score
		self._min_eval = Score.checkmate(chess.BLACK) if use_score else -inf
		self._max_eval = Score.checkmate(chess.WHITE) if use_score else inf
		super().__init__(test_case.depth, maxing = test_case.maxing, pruning=pruning, verbose=verbose)

	def children(self) :
		return list(self.stack[-1][1]) if len(self.stack[-1]) > 1 else []

	def eval(self) :
		return self.stack[-1][0]

	def apply(self, choice) :
		self.stack.append(choice)

	def unapply(self) :
		self.stack.pop()

	@property
	def min_eval(self) :
		return self._min_eval

	@property
	def max_eval(self) :
		return self._max_eval

	def inc_eval(self, e) :
		if self.use_score :
			return e.inc()
		else :
			return e

	def __str__(self) :
		return str(self.stack[-1])