MAKEFLAGS += --silent

cpp_files := $(wildcard *.cpp)
h_files := $(wildcard *.h)

all : bin/cpp-chess

bin/cpp-chess : $(cpp_files) $(h_files)
	mkdir -p bin
	g++ $(cpp_files) -O3 -o bin/cpp-chess -std=c++11 -stdlib=libc++ -lprofiler

profile : bin/cpp-chess
	LD_PRELOAD=/usr/local/lib/libprofiler.dylib CPUPROFILE=profile.prof bin/cpp-chess
	pprof --pdf bin/cpp-chess profile.prof > profile.pdf

clean : 
	rm -rf bin/*

test : all
	python test.py

test_seq : all
	python test_seq.py

count_positions : all
	python count_positions.py

.PHONY: all clean profile

