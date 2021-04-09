from timer import Timer
from big_array import BigArray

Timer.start()
arr = BigArray('test', 1 << 30)
Timer.end("Array creation")

Timer.start()
for i in range(len(arr)) :
	arr[i] = i % 256
Timer.end("Array filling")

Timer.start()
arr.flush()
Timer.end("Array writing")