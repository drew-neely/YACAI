from math import inf
import random
import chess
import os, sys
from matplotlib import use

from matplotlib.pyplot import get
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from eval import get_eval
from score import Score

random.seed(1234)

class TestCase :

	all_tests = []

	def __init__(self, res, maxing) :
		self.res = res
		self.maxing = maxing
		TestCase.all_tests.append(self)

class ArrTestCase(TestCase) :

	def __init__(self, arr, res, maxing) :
		super().__init__(res, maxing)
		self.arr = arr
		self.depth = ArrTestCase.get_dims(arr)
		if self.depth is None :
			raise ValueError("ArrTestCase test case cannot use variable dimensional input")

	# find the dimensions of the array - None if not constant dimension
	@staticmethod
	def get_dims(arr) :
		if isinstance(arr, (int,float)) :
			return 0
		dims = [ArrTestCase.get_dims(sub_arr) for sub_arr in arr]
		if None in dims :
			return None
		dims = set(dims)
		if len(dims) != 1 :
			return None
		return list(dims)[0] + 1

	@staticmethod
	def random(depth, width=[1,2,2,2,3,3,3,4,4,4,5,5,5,6,6,10]) :
		return ArrTestCase(ArrTestCase.random_tree(depth, width), None, maxing = random.choice([True, False]))


	@staticmethod
	def random_tree(depth, width) :
		if depth == 0 :
			return random.randint(-99, 99)
		return [TestCase.random_tree(depth - 1, width = width) for _ in range(random.choice(width))]

	def __str__(self) :
		return f"<maxing={self.maxing}, d={self.depth}, res={self.res}, arr={str(self.arr)[:200]}>"



####

class TupleTestCase(TestCase) :

	def __init__(self, tup, res, maxing, depth = inf, use_score = False, fen = None):
		super().__init__(res, maxing)
		if tup == None :
			assert fen != None , "TupleTestCase may be specified with tup=None to delay generation till usage, but fen must be specified"
		self._tup = tup
		self.depth = depth
		self.use_score = use_score
		self.fen = fen

	@property
	def tup(self) :
		if self._tup is None :
			self._tup = TupleTestCase._from_board(chess.Board(self.fen), self.depth)
		return self._tup

	@staticmethod
	def from_fen(fen, res, depth) :
		board = chess.Board(fen)
		return TupleTestCase(None, res, board.turn == chess.WHITE, depth=depth, use_score=True, fen=fen)

	@staticmethod
	def from_board(board, res, depth) :
		return TupleTestCase(None, res, board.turn == chess.WHITE, depth = depth, use_score=True, fen=board.fen())

	@staticmethod
	def _from_board(board, depth) :
		value = get_eval(board)
		if depth == 0 :
			return (value, )
		moves = list(board.legal_moves)
		if len(moves) == 0 :
			return (value, )
		children = []
		for move in moves :
			board.push(move)
			children.append(TupleTestCase._from_board(board, depth - 1))
			board.pop()
		return (value, tuple(children))

	def __str__(self) :
		return f"<maxing={self.maxing}, d={self.depth}, res={self.res}, arr={str(self.tup)[:200]}>"


#######################################
###### Trivial dimension 0 test cases
#######################################

ArrTestCase(-10, -10, maxing=True)
ArrTestCase(-10, -10, maxing=False)
ArrTestCase(10, 10, maxing=True)
ArrTestCase(10, 10, maxing=False)
ArrTestCase(0, 0, maxing=True)
ArrTestCase(0, 0, maxing=True)

#######################################
###### Trivial dimension 1 test cases
#######################################

ArrTestCase([-10, 10], 10, maxing=True)
ArrTestCase([-10, 10], -10, maxing=False)
ArrTestCase([10, 0, -10, 100, -100], 100, maxing=True)
ArrTestCase([10, 0, -10, 100, -100], -100, maxing=False)

#######################################
###### 2 dimensional test cases
#######################################

ArrTestCase([[-10, 10], [9, -9]], -9, maxing=True)
ArrTestCase([[9, -9], [-10, 10]], -9, maxing=True)
ArrTestCase([[-10, 10], [9, -9]], 9, maxing=False)
ArrTestCase([[9, -9], [-10, 10]], 9, maxing=False)

ArrTestCase([[-10, 10], [-15, 15, 3, 4, -7], [9, -9], [1, -1, -6, 6], [-100, 10000]], -6, maxing=True)
ArrTestCase([[-10, 10], [-15, 15, 3, 4, -7], [9, -9], [1, -1, -6, 6], [-100, 10000]], 6, maxing=False)

ArrTestCase([[0,0,0], [0,0,0], [0,0,1]], 0, maxing=False)
ArrTestCase([[0,0,0], [0,0,0], [0,0,1]], 0, maxing=True)


#######################################
###### 3 dimensional test cases
#######################################

ArrTestCase([
	[[-10, 10], [9, -9]], # 9
	[[-10, 10], [-15, 15, 3, 4, -7], [9, -9], [1, -1, -6, 6], [-100, 10000]], # 6
	[[78, 24,23], [1], [-1, -54, 0]], # 0
	[[0]] # 0
], 9, maxing=True)

ArrTestCase([
	[[-10, 10], [9, -9]], # 9
	[[-10, 10], [-15, 15, 3, 4, -7], [9, -9], [1, -1, -6, 6], [-100, 10000]], # 6
	[[78, 24,23], [1], [-1, -54, 0]], # 0
	[[0]] # 0
], 9, maxing=True)

#######################################
###### Random test cases
#######################################

# for i in range(5) : ArrTestCase.random(2)
# for i in range(5) : ArrTestCase.random(3)
# for i in range(5) : ArrTestCase.random(4)
# for i in range(5) : ArrTestCase.random(5)
# ArrTestCase.random(15, width=[2])
# ArrTestCase.random(15, width=[2,3])
# ArrTestCase.random(25, width=[2])


#######################################
###### Chess -> tuple test cases
#######################################

# . . . . . k . .
# . . P . . . . .
# . . . . . K . .
# . . . . . . . .
# . . . . . . . .
# . . . . . . . .
# . . . . . . . .
# . . . . . . . .
ctc1 = TupleTestCase.from_fen("5k2/2P5/5K2/8/8/8/8/8 w - - 0 1", Score.mate_in(1, chess.WHITE), 2)

# . . . . . k . .
# . . Q . . . . .
# . . . . K . . .
# . . . . . . . .
# . . . . . . . .
# . . . . . . . .
# . . . . . . . .
# . . . . . . . .
ctc2 = TupleTestCase.from_fen("5k2/2Q5/4K3/8/8/8/8/8 b - - 0 1", Score.mate_in(4, chess.WHITE), 5)


# . . . . k . . .
# . . P . . . p .
# . . . . . p P p
# . . . . p P . P
# . . . . P . . K
# . . . . . . . .
# . . . . . . . .
# . . . . . . . .
ctc3 = TupleTestCase.from_fen("4k3/2P3p1/5pPp/4pP1P/4P2K/8/8/8 b - - 0 1", None, 4)

# . . . . k . . .
# . . p p p p p p
# . . . . . . . .
# p p . . . . . .
# . . . P . . . .
# . . K . . . . .
# . . . . P . . .
# . . . . . . . .
ctc4 = TupleTestCase.from_fen("4k3/2pppppp/8/pp6/3P4/2K5/4P3/8 b - - 1 3", None, 2)

# . . . . k . . .
# . . . p p p p p
# . . . . . . . .
# p p p . . . . .
# . . . P . . . .
# . . K . . . . .
# . . . . P . . .
# . . . . . . . .
ctc5 = TupleTestCase.from_fen("4k3/3ppppp/8/ppp5/3P4/2K5/4P3/8 w - c6 0 4", None, 2)


# . . . . k . . .
# . . p . . . . .
# . . . . . . . .
# . . . . . . . .
# . . . P . . . .
# . . K . . . . .
# . . . . . . . .
# . . . . . . . .
ctc6 = TupleTestCase.from_fen("4k3/2p5/8/8/3P4/2K5/8/8 b - - 1 3", None, 2)

# . . . . k . . .
# . . . . . . . .
# . . . . . . . .
# . . p . . . . .
# . . . P . . . .
# . . K . . . . .
# . . . . . . . .
# . . . . . . . .
ctc6 = TupleTestCase.from_fen("4k3/8/8/2p5/3P4/2K5/8/8 w - - 0 4", None, 1)

# . . . . . . . .
# . . . . . . . .
# . . . k . . . .
# . Q . . . . . K
# . . . . . . . .
# . . . . . . . .
# . . . . P . . .
# q . . . . . . .
ctc7 = TupleTestCase.from_fen("8/8/3k4/1Q5K/8/8/4P3/q7 b - - 0 15", None, 2) # TODO: Debug this

print("Created all test cases (Some may use delayed generation)\n")