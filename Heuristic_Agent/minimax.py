from math import inf

from eval import get_eval

# Each minimax search is done as a class so that stats can be collected
# Minimax is not intended to be used on it's own - it must be subclassed
# 	The following methods must be implemented by the subclass. This is so 
# 	that the test bench can be attached.
# 		- self.children()
# 		- self.eval()
# 		- self.apply()
# 		- self.unapply()
class Minimax :

	def __init__(self, node, depth, alpha=-inf, beta=inf, maxing=True, pruning=True):
		self.node = node
		self.search_depth = depth
		self.search_alpha = alpha
		self.search_beta = beta
		self.search_maxing = maxing
		self.pruning = pruning
		
		# perf stats
		self.num_evaled = 0

		# perform the search
		(self.best_quality, self.best_path, _, _) = self.search(depth, alpha, beta, maxing)

	# returns (<best achievable quality>, [<choices to get to best state>])
	def search(self, depth, alpha, beta, maxing) :
		choices = self.children()
		if depth == 0 or not choices :
			self.num_evaled += 1
			return (self.eval(), [], alpha, beta)

		best_quality = -inf if maxing else inf
		best_path = None
		best_choice = None
		for choice in choices:
			# print(''.join(["\t"]*(3-depth)) + move.uci(), best_quality)
			self.apply(choice)
			(quality, path, alpha, beta) = self.search(depth - 1, alpha, beta, not maxing)
			if (maxing and quality >= best_quality) or (not maxing and quality <= best_quality) :
				best_quality = quality
				best_path = path
				best_choice = choice
			self.unapply()
			if self.pruning :
				if (maxing and best_quality >= beta) or (not maxing and best_quality <= alpha) :
					break
				if maxing and best_quality > alpha :
					alpha = best_quality
				elif not maxing and best_quality < beta :
					beta = best_quality
				# if beta <= alpha :
				# 	break
		# print(''.join(["\t"]*(3-depth)) + "BEST:", best_quality, best_choices)
		return (best_quality, [best_choice] + best_path, alpha, beta)

	##########################################
	####### Abstract method declarations
	##########################################

	def children(self) :
		raise NotImplementedError()

	def eval(self) :
		raise NotImplementedError()

	def apply(self, choice) :
		raise NotImplementedError()

	def unapply(self) :
		raise NotImplementedError()

	##########################################
	####### Debug methods
	##########################################

	def dump(self) :
		print("Minimax search dump:")
		print(f"num_evaled = {self.num_evaled}")
		print(f"depth = {self.search_depth}, maxing = {self.search_maxing}, best choice = {self.best_path[0]}")
		print(f"best path = {self.best_path}")
		print(f"position eval = {self.eval()}")
		print(f"best eval = {self.best_quality}")
		print()