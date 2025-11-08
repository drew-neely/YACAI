import sys
f = open(sys.argv[1])
b = open(sys.argv[1] + ".lf", "w")
for line in f :
    b.write(line)
f.close()
b.close()