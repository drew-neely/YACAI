import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from minimax import Minimax

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

	def __str__(self) :
		return str(self.stack[-1])

class TupMinimax(Minimax) :
	def __init__(self, test_case, pruning=True, verbose=False):
		self.test_case = test_case
		self.stack = [test_case.tup]
		super().__init__(test_case.depth, maxing = test_case.maxing, pruning=pruning, verbose=verbose)

	def children(self) :
		return list(self.stack[-1][1]) if len(self.stack[-1]) > 1 else []

	def eval(self) :
		return self.stack[-1][0]

	def apply(self, choice) :
		self.stack.append(choice)

	def unapply(self) :
		self.stack.pop()

	def __str__(self) :
		return str(self.stack[-1])