from math import inf, exp
from time import time
import numpy as np

from eval import get_eval

# Each minimax search is done as a class so that stats can be collected
# Minimax is not intended to be used on it's own - it must be subclassed
# 	The following methods must be implemented by the subclass. This is so 
# 	that the test bench can be attached.
# 		- self.children()
# 		- self.eval()
# 		- self.apply(choice)
# 		- self.unapply()
#       - self.min_eval() (@property) # the minimum evaluation possible
#       - self.max_eval() (@property) # the maximum evaluation possible
#       - inc_eval() # returns resultant eval from passing eval back one branch in minimax tree
#   Optional
#       - record(quality, depth, maxing) # not required - may be used to record a result into a transposition table
#       - lookup(depth, maxing) # not required - may be used to check in transposition table - returns quality or None
#   Debug methods - optional
#       - dump()
class Minimax :

	def __init__(self, depth, timeout=None, alpha=None, beta=None, maxing=True, pruning=True, it_deepening = True, verbose = False):
		if alpha == None :
			self.search_alpha = self.min_eval
		else :
			self.search_alpha = alpha

		if beta == None :
			self.search_beta = self.max_eval
		else :
			self.search_beta = beta

		assert timeout is not None or it_deepening, "Timeout cannot be specified without iterative deepening" 
		self.timeout = timeout # number of seconds to search for
		self.search_depth = depth
		self.search_maxing = maxing
		self.pruning = pruning
		self.it_deepening = it_deepening
		self.verbose = verbose
		
		# perf stats
		self.num_evaled = 0
		self.search_time = 0 # in seconds

		# perform the search
		if self.it_deepening :
			(self.best_quality, self.best_choice) = self.it_deepening_search(depth, self.search_alpha, self.search_beta, maxing)
		else :
			(self.best_quality, self.best_choice) = self.search(depth, self.search_alpha, self.search_beta, maxing)

	def it_deepening_search(self, depth, alpha, beta, maxing) :
		if depth == 0 :
			return self.search(0, alpha, beta, maxing)
		# will go to at least depth depth, but keep going until self.timout time has passed
		res = None
		d = 1
		times = []
		while d <= depth :
			res = self.search(d, alpha, beta, maxing)
			times.append(self.search_time)
			print(f"d={d}, time={self.search_time}")
			d += 1
		if self.timeout is not None :

			# x, y = np.arange(1,d), np.array(times)
			# print(x)
			# print(y)
			# b, a = np.polyfit(x, np.log(y), 1, w=np.sqrt(y))
			# prediction = exp(a) * exp(b * d)
			# print(prediction)

			while self.search_time < self.timeout :
				res = self.search(d, alpha, beta, maxing)
				print(f"d={d}, time={self.search_time}")
				times.append(self.search_time)
				self.search_depth = d
				d += 1
		return res
		

	# returns (<best achivable quality>, <best choice>)
	def search(self, depth, alpha, beta, maxing) :
		start_time = time()
		if self.verbose : print(f"-- Starting base-level search: maxing = {maxing}, (a,b) = {(alpha, beta)} -- {self}")
		if depth == 0 :
			quality = self.eval()
			if self.verbose : print(f"---- Leaf Node {self} ===> {quality}")
			self.search_time += time() - start_time
			return (quality, None)
		choices = self.children()
		best_quality = self.min_eval if maxing else self.max_eval
		best_choice = None
		for choice in choices:
			self.apply(choice)
			quality = self.inc_eval(self._search(depth - 1, alpha, beta, not maxing))
			self.unapply()
			if (maxing and quality > best_quality) or (not maxing and quality < best_quality) :
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
		self.search_time += time() - start_time
		return (best_quality, best_choice)


	
	# returns best achievable quality - returning best choices is incompatible with alpha beta pruning
	def _search(self, depth, alpha, beta, maxing) :
		lookup_res = self.lookup(depth, maxing)
		if lookup_res is not None :
			if depth == 0 :
				self.num_evaled += 1
			return lookup_res
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
		self.record(best_quality, depth, maxing)
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

	# May be implemented by subclass - by default does nothing
	def record(self, quality, depth, maxing) :
		pass

	# May be implemented by subclass - by default does nothing
	def lookup(self, depth, maxing) :
		return None

	##########################################
	####### Debug methods
	##########################################

	# May be implemented by subclass - by default does nothing
	def dump(self) :
		pass