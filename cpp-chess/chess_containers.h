#pragma once

#include <stdint.h>
#include <stdio.h>
#include <cmath>
#include <assert.h>
#include <string.h>

#include "board.h"


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


/*
	This is a very simple implementation of a set pieces currently on a board.
	Adding to a field which is equal to 15, or removing from a field which is 0,
	will result in undefined/invalid behavior. A real game of chess will never have
	a value larger than 10 in any field. Also, each field is easily represented as
	one hex digit per field.
	The encoding of the 64 bit compositionId is :
	[3:0]   = number of white pawns
	[7:4]   = number of white knights
	[11:8]  = number of white bishops (total - light and dark square)
	[15:12] = number of white rooks
	[19:16] = number of white queens
	[23:20] = number of white dark-square bishops
	[31:24] = unused (0)
	[35:32] = number of black pawns
	[39:36] = number of black knights
	[43:40] = number of black bishops (total - light and dark square)
	[47:44] = number of black rooks
	[51:48] = number of black queens 
	[55:52] = number of black dark-square bishops
	[62:56] = unused (0)
	[63]    = insuficient material for checkmate (0 for sufficient material, 1 for insuficient material)
*/ 
struct Composition {

	uint64_t compositionId;

	Composition() : compositionId(0x00112228'00112228) {}; // Init with composition of starting position
	Composition(uint64_t comp) : compositionId(comp) { encodeInsufficientMaterial(); };

	Composition(BoardState& state);

	void add(uint8_t pid, uint8_t sq_color);
	void remove(uint8_t pid, uint8_t sq_color) ;

	// Calculates if the composition represents a draw by insufficient material (Following USCF rules)
	// and sets the corresponding bit in the encoding
	void encodeInsufficientMaterial();

	// returns if the position represents a draw by insufficient material according to the corresponding
	// bit in the encoding
	bool isInsufficientMaterial() {
		return (compositionId & 0x80000000'00000000) != 0;
	}

	bool operator==(Composition& other) const {
		return this->compositionId == other.compositionId;
	}
	bool operator!=(Composition& other) const {
		return this->compositionId != other.compositionId;
	}


};

template<class Value>
struct TransTable {
	
	struct Entry {
		uint64_t key;
		Value value;
	};

	size_t capacity;
	Entry* data;

	const size_t hash_mask;

	TransTable(size_t capacity) : capacity(capacity), hash_mask(capacity - 1) {
		assert((capacity & (capacity - 1)) == 0); // Check that capacity is a power of 2
		assert(sizeof(Entry) % 8 == 0); // This should always be true, this is just here to make sure I understand C++
		
		data = (Entry*) malloc(sizeof(Entry) * capacity);
		// printf("cons data = %p\n", data);
		memset(data, 0, sizeof(Entry) * capacity); // zero the memory out
	}

	bool contains(uint64_t key) {
		return data[key & hash_mask].key == key;
	}

	Value get(uint64_t key) { // Undefined behavior if contains(key) == false
		return data[key & hash_mask].value;
	}

	void set(uint64_t key, Value value) {
		data[key & hash_mask] = { key, value };
	}

	// TODO : Appropriately delete data
	
	// ~TransTable() { printf("dest data = %p\n", data); free(data); } // release memory on deletion

};

