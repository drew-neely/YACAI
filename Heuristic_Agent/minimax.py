from math import inf, exp
from time import time
from util import exponential_regression_eval

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
#       - is_solved_eval(quality) # not required - may be used to terminate it_deepening early if quality represents a solved search that doesn't require more investigation
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

		assert timeout is None or it_deepening, "Timeout cannot be specified without iterative deepening" 
		self.timeout = timeout # number of seconds to search for
		self.search_depth = depth
		self.search_maxing = maxing
		self.pruning = pruning
		self.it_deepening = it_deepening
		self.verbose = verbose
		
		# perf stats
		self.num_evaled = 0
		self.search_time = 0 # in seconds
		self.termination_reason = None

		# perform the search
		if self.it_deepening :
			(self.best_quality, self.best_choice) = self.it_deepening_search(depth, self.search_alpha, self.search_beta, maxing)
		else :
			(self.best_quality, self.best_choice) = self.search(depth, self.search_alpha, self.search_beta, maxing)

	def it_deepening_search(self, depth, alpha, beta, maxing) :
		# will go to at least depth depth, but keep going until self.timout time has passed

		res = None
		cutoff_at_depth = depth != 0
		assert cutoff_at_depth or self.timeout is not None, "it_deepening cannot be executed without stopping condition"
		times = []
		d = 0 # last depth searched
		while True :
			if self.timeout is None and d >= depth : # No timeout exists and depth reached
				self.termination_reason = "Reached specified depth"
				break
			if self.timeout is not None and (not cutoff_at_depth or d >= depth) : # There is time limit and (depth has been reached or there is no depth limit)
				if self.search_time >= self.timeout : # test if time already exceeded
					self.termination_reason = "Search time exceeded"
					break
				if len(times) >= 2 : # predict the time the next search will end at if there's enough data points
					prediction = exponential_regression_eval(range(1,d+1), times, d+1)
					if prediction > self.timeout :
						self.termination_reason = f"Predicting to exceed search time ({round(prediction*100)/100}s > {self.timeout}s)"
						break
			
			# search depth d+1
			res = self.search(d+1, alpha, beta, maxing)
			d += 1

			# record time and update search depth
			self.search_depth = max(self.search_depth, d)
			times.append(self.search_time)
			print(f"time after depth {d} = {self.search_time}")

			# check if search has stalled
			if self.is_solved_eval(res[0]) :
				self.termination_reason = "Search has stalled"
				break
			
		assert res is not None
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

	def is_solved_eval(self, quality) :
		return False

	##########################################
	####### Debug methods
	##########################################

	# May be implemented by subclass - by default does nothing
	def dump(self) :
		pass