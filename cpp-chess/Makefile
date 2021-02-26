# MAKEFLAGS += --silent

cpp_files := $(wildcard *.cpp)
h_files := $(wildcard *.h)

all : bin/cpp-chess

bin/cpp-chess : $(cpp_files) $(h_files)
	mkdir -p bin
	g++ $(cpp_files) -O3 -o bin/cpp-chess

clean : 
	rm -rf bin/*

test : all
	python test.py

test_seq : all
	python test_seq.py

.PHONY: all clean

