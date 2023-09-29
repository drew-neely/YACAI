# MAKEFLAGS += --silent

cpp_files := $(wildcard *.cpp)
h_files := $(wildcard *.h)
test_cpp_files := $(wildcard tests/*.cpp)
test_h_files := $(wildcard tests/*.h)

all : bin/cpp-chess bin/cpp-chess-wprof bin/cpp-chess-test 

###############################
###### compile chess engine
###############################
bin/cpp-chess : $(cpp_files) $(h_files) $(test_cpp_files) $(test_h_files)
	mkdir -p bin
	g++ $(cpp_files) $(test_cpp_files) -O3 -o bin/cpp-chess -std=c++2a -Werror -fcoroutines -fPIC --shared

###############################
###### testing
###############################

bin/cpp-chess-test : $(cpp_files) $(h_files) $(test_cpp_files) $(test_h_files)
	mkdir -p bin
	g++ $(cpp_files) $(test_cpp_files) -O3 -g -o bin/cpp-chess-test -DTESTING -std=c++2a -Werror -fcoroutines

test : bin/cpp-chess-test 
	./bin/cpp-chess-test 

###############################
###### Profiling with testing
###############################

bin/cpp-chess-wprof : $(cpp_files) $(h_files)
	mkdir -p bin
	g++ $(cpp_files) $(test_cpp_files) -O3 -g -o bin/cpp-chess-wprof -DTESTING -fno-pie -std=c++2a -lprofiler -fcoroutines

# create various perf files

bin/profile.prof : bin/cpp-chess-wprof
	LD_PRELOAD=/usr/local/lib/libprofiler.dylib CPUPROFILE=bin/profile.prof bin/cpp-chess-wprof

bin/profile.callgrind : bin/cpp-chess-wprof bin/profile.prof 
	pprof --callgrind bin/cpp-chess-wprof bin/profile.prof > bin/profile.callgrind

bin/profile.pdf : bin/profile.prof
	pprof --pdf bin/cpp-chess-wprof bin/profile.prof > bin/profile.pdf

# short cut commands to make files

callgrind : bin/profile.callgrind
	qcachegrind bin/profile.callgrind

pdf : bin/profile.pdf

profile: pdf callgrind


###############################
###### MISC
###############################

clean : 
	rm -rf bin/*

test_seq : all
	python test_seq.py

count_positions : bin/cpp-chess
	python count_positions.py

.PHONY: all clean callgrind pdf profile callgrind

