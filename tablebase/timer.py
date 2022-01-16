from time import time

start_times = []

class Timer :

	@staticmethod
	def start() :
		global start_times
		start_times.append(time());
	
	@staticmethod
	def end(msg=None) :
		global start_times
		t = time()
		assert len(start_times) != 0
		t = t - start_times.pop()
		if msg :
			print(f'Time elapsed: {t:5.2}s - {msg}')
		else :
			print(f'Time elapsed: {t:5.2}s')