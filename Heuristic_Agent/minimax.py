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
#       - self.min_eval() (@property) # the minimum evaluation possible
#       - self.max_eval() (@property) # the maximum evaluation possible
#       - inc_eval() # returns resultant eval from passing eval back one branch in minimax tree
#   Optionally, some debug methods may be implemented
#       - dump()
class Minimax :

	def __init__(self, depth, alpha=None, beta=None, maxing=True, pruning=True, verbose = False):
		if alpha == None :
			self.search_alpha = self.min_eval
		else :
			self.search_alpha = alpha

		if beta == None :
			self.search_beta = self.max_eval
		else :
			self.search_beta = beta

		self.search_depth = depth
		self.search_maxing = maxing
		self.pruning = pruning
		self.verbose = verbose
		
		# perf stats
		self.num_evaled = 0

		# perform the search
		(self.best_quality, self.best_choice) = self.search(depth, self.search_alpha, self.search_beta, maxing)

	# returns (<best achivable quality>, <best choice>)
	def search(self, depth, alpha, beta, maxing) :
		if self.verbose : print(f"-- Starting base-level search: maxing = {maxing}, (a,b) = {(alpha, beta)} -- {self}")
		if depth == 0 :
			quality = self.eval()
			if self.verbose : print(f"---- Leaf Node {self} ===> {quality}")
			return (quality, None)
		choices = self.children()
		best_quality = self.min_eval if maxing else self.max_eval
		best_choice = None
		for choice in choices:
			self.apply(choice)
			quality = self.inc_eval(self._search(depth - 1, alpha, beta, not maxing))
			self.unapply()
			if (maxing and quality >= best_quality) or (not maxing and quality <= best_quality) :
				best_quality = quality
				best_choice = choice
			if self.pruning :
				if maxing and best_quality > alpha :
					if self.verbose : print(f"alpha = {best_quality} after choice {choice}")
					alpha = best_quality
				if not maxing and best_quality < beta :
					if self.verbose : print(f"beta = {best_quality} after choice {choice}")
					beta = best_quality
		if self.verbose : print(f"---- Ending base-level search: {self} ===> {(best_quality, best_choice)}")
		return (best_quality, best_choice)


	
	# returns best achievable quality - returning best choices is incompatible with alpha beta pruning
	def _search(self, depth, alpha, beta, maxing) :
		choices = self.children()
		if depth == 0 or not choices :
			self.num_evaled += 1
			quality = self.eval()
			if self.verbose : print(f"---- Leaf Node {self} ===> {quality}")
			return quality
		
		if self.verbose : print(f"-- Starting search: maxing = {maxing}, (a,b) = {(alpha, beta)} -- {self}")

		if maxing : # Maximizing

			best_quality = self.min_eval
			
			for choice in choices:

				self.apply(choice)
				best_quality = max(best_quality, self._search(depth - 1, alpha, beta, not maxing))
				self.unapply()

				if self.pruning :
					if best_quality >= beta :
						if self.verbose : 
							print(f"*Pruning after {choice}")
							print(f"\tmaxing = {maxing}, (a,b) = {(alpha, beta)}, best_quality = {best_quality}")
						break
					if best_quality > alpha :
						if self.verbose : print(f"alpha = {best_quality} after choice {choice}")
						alpha = best_quality
		
		else : # Minimizing player
			best_quality = self.max_eval
			
			for choice in choices:

				self.apply(choice)
				best_quality = min(best_quality, self._search(depth - 1, alpha, beta, not maxing))
				self.unapply()

				if self.pruning :
					if best_quality <= alpha :
						if self.verbose : 
							print(f"*Pruning after {choice}")
							print(f"\tmaxing = {maxing}, (a,b) = {(alpha, beta)}, best_quality = {best_quality}")
						break
					if best_quality < beta :
						if self.verbose : print(f"beta = {best_quality} after choice {choice}")
						beta = best_quality

		if self.verbose : print(f"---- Ending search {self} ===> {best_quality}")
		return self.inc_eval(best_quality)

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

	@property
	def min_eval(self) :
		raise NotImplementedError()

	@property
	def max_eval(self) :
		raise NotImplementedError()

	def inc_eval(self, score) :
		raise NotImplementedError()

	##########################################
	####### Debug methods
	##########################################