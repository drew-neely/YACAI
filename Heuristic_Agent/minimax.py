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

	def __init__(self, depth, alpha=-inf, beta=inf, maxing=True, pruning=True, verbose = False):
		self.search_depth = depth
		self.search_alpha = alpha
		self.search_beta = beta
		self.search_maxing = maxing
		self.pruning = pruning
		self.verbose = verbose
		
		# perf stats
		self.num_evaled = 0

		# perform the search
		(self.best_quality, self.best_path, _, _) = self.search(depth, alpha, beta, maxing)

	# returns (<best achievable quality>, [<choices to get to best state>])
	def search(self, depth, alpha, beta, maxing) :
		if self.verbose : print(f"-- Starting search: maxing = {maxing}, (a,b) = {(alpha, beta)} -- {self}")
		choices = self.children()
		if depth == 0 or not choices :
			self.num_evaled += 1
			quality = self.eval()
			if self.verbose : print(f"---- Evauluating {self} ===> {quality}")
			return (quality, [], alpha, beta)
		
		if maxing : # Maximizing

			best_quality = -inf
			best_path = None
			best_choice = None
			
			for choice in choices:
				self.apply(choice)
				(quality, path, _, _) = self.search(depth - 1, alpha, beta, not maxing)

				if quality >= best_quality :
					best_quality = quality
					best_path = path
					best_choice = choice

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
			best_quality = inf
			best_path = None
			best_choice = None
			
			for choice in choices:
				self.apply(choice)
				(quality, path, _, _) = self.search(depth - 1, alpha, beta, not maxing)

				if quality <= best_quality :
					best_quality = quality
					best_path = path
					best_choice = choice

				self.unapply()

				if self.pruning :
					if best_quality <= alpha :
						if self.verbose : 
							print(f"*Pruning after {choice}")
							print(f"\tmaxing = {maxing}, (a,b) = {(alpha, beta)}, best_quality = {best_quality}")
						break
					if maxing and best_quality > alpha :
						if self.verbose : print(f"alpha = {best_quality} after choice {choice}")
						alpha = best_quality
					elif not maxing and best_quality < beta :
						if self.verbose : print(f"beta = {best_quality} after choice {choice}")
						beta = best_quality

		if self.verbose : print(f"---- Ending search {self} ===> {best_quality}")
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