import time

PERF_DATA = True

class Feature :
	
	def __init__(self) :
		if PERF_DATA :
			self.time_running = 0
			self.extract_method = self.extract_with_perf
		else :
			self.time_running = None
			self.extract_method = self._extract

	def extract(self, game, player_color) :
		return self.extract_method(game, player_color)

	def extract_with_perf(self, game, player_color):
		start_time = time.time()
		res = self._extract(game, player_color)
		self.time_running += time.time() - start_time
		return res

	# must be implemented at the subclass level - no abstract methods in python
	def _extract(self, game, player_color) :
		raise NotImplementedError()

