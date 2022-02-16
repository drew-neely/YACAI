# MAKEFLAGS += --silent

cpp_files := $(wildcard *.cpp)
h_files := $(wildcard *.h)

all : bin/cpp-chess bin/cpp-chess-wprof

bin/cpp-chess : $(cpp_files) $(h_files)
	mkdir -p bin
	g++ $(cpp_files) -O3 -o bin/cpp-chess -std=c++11 -stdlib=libc++

bin/cpp-chess-wprof : $(cpp_files) $(h_files)
	mkdir -p bin
	g++ $(cpp_files) -O3 -g -o bin/cpp-chess-wprof -fno-pie -std=c++11 -stdlib=libc++ -lprofiler

run : bin/cpp-chess
	./bin/cpp-chess

bin/profile.prof : bin/cpp-chess-wprof
	LD_PRELOAD=/usr/local/lib/libprofiler.dylib CPUPROFILE=bin/profile.prof bin/cpp-chess-wprof

bin/profile.callgrind : bin/cpp-chess-wprof bin/profile.prof 
	pprof --callgrind bin/cpp-chess-wprof bin/profile.prof > bin/profile.callgrind

bin/profile.pdf : bin/profile.prof
	pprof --pdf bin/cpp-chess-wprof bin/profile.prof > bin/profile.pdf

callgrind : bin/profile.callgrind
	qcachegrind bin/profile.callgrind

pdf : bin/profile.pdf

profile: pdf callgrind

clean : 
	rm -rf bin/*

test : all
	python test.py

test_seq : all
	python test_seq.py

count_positions : all
	python count_positions.py

.PHONY: all clean callgrind pdf profile callgrind

