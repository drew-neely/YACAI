import sys
f = open(sys.argv[1])
n = int(sys.argv[2])

i = 0
while i < n*3 :
    f.readline()
    i += 1
print(f.readline()[:-1])
print(f.readline()[:-1])
print(f.readline()[:-1])
    