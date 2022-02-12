#pragma once

#include <stdint.h>
#include <stdio.h>


/*
	This is a very simple implementation of a set that can store values from 0-63.
	Because membership can be store in a single 64 bit bitmap this performs much
	better than a regular std:: by a huge factor
*/
struct SquareSet {

	uint64_t bitmap;

	SquareSet() : bitmap(0) {}

	void insert(uint8_t sq) {
		bitmap |= (uint64_t) 1 << sq;
	}

	bool contains(uint8_t sq) {
		return (bitmap & ((uint64_t) 1 << sq)) != 0;
	}

};


