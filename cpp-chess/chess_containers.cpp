#include <stdint.h>
#include <stdio.h>

#include "board.h"
#include "chess_containers.h"

Composition::Composition(BoardState& state) : compositionId(0) {
	for(uint8_t sq = 0; sq < 64; sq++) {
		uint8_t pid = state.squares[sq];
		if(pid != 0 && piece(pid) != KING) {
			add(pid, square_color(sq));
		}
	}
	encodeInsufficientMaterial();
}

void Composition::add(uint8_t pid, uint8_t sq_color) {
	uint8_t idx = ((pid & BLACK) << 1) | (piece(pid) << 2);
	compositionId = (((compositionId >> idx) + 1) << idx) | (compositionId & ((1l << idx) -1));
	if(sq_color == DARK_SQUARE && piece(pid) == BISHOP) {
		idx = ((pid & BLACK) << 1) | 20;
		compositionId = (((compositionId >> idx) + 1) << idx) | (compositionId & ((1l << idx) -1));
	}
	encodeInsufficientMaterial();
}

void Composition::remove(uint8_t pid, uint8_t sq_color) {
	uint8_t idx = ((pid & BLACK) << 1) | (piece(pid) << 2);
	compositionId = (((compositionId >> idx) - 1) << idx) | (compositionId & ((1l << idx) -1));
	if(sq_color == DARK_SQUARE && piece(pid) == BISHOP) {
		idx = ((pid & BLACK) << 1) | 20;
		compositionId = (((compositionId >> idx) - 1) << idx) | (compositionId & ((1l << idx) -1));
	}
	encodeInsufficientMaterial();
}

uint8_t Composition::getNumPieces(uint8_t pid) {
	uint8_t idx = ((pid & BLACK) << 1) | (piece(pid) << 2);
	return (compositionId >> idx) & 0xF;
}

#define set_insuficient()   compositionId |= 0x80000000'00000000
#define clear_insuficient() compositionId &= 0x7FFFFFFF'FFFFFFFF

const uint64_t K_k      = 0x00000000'00000000;
const uint64_t KB_k     = 0x00000000'00000100; // bishop agnostic
const uint64_t K_kb     = 0x00000100'00000000; // bishop agnostic
const uint64_t KN_k     = 0x00000000'00000010;
const uint64_t K_kn     = 0x00000010'00000000;
const uint64_t KB_kn    = 0x00000010'00000100; // bishop agnostic
const uint64_t KN_kb    = 0x00000100'00000010; // bishop agnostic
const uint64_t KN_kn    = 0x00000010'00000010;
const uint64_t KNN_k    = 0x00000000'00000020;
const uint64_t K_knn    = 0x00000020'00000000;
const uint64_t KdB_kdb  = 0x00100100'00100100; // bishop type required
const uint64_t KlB_klb  = 0x00000100'00000100; // bishop type required
const uint64_t KdBdB_k  = 0x00200200'00000000; // bishop type required
const uint64_t K_kdbdb  = 0x00000000'00200200; // bishop type required
const uint64_t KlBlB_k  = 0x00000200'00000000; // bishop type required
const uint64_t K_klblb  = 0x00000000'00000200; // bishop type required

void Composition::encodeInsufficientMaterial() {
	if((compositionId & 0x000FF00F'000FF00F) != 0) { // If there is at least 1 queen, rook, or pawn on the board, short circuit other checks
		clear_insuficient();
	}
	uint64_t bishopAgnosticCompositionId = compositionId & 0x000FFFFF'000FFFFF;
	uint64_t clearCompositionId          = compositionId & 0x00FFFFFF'00FFFFFF;

	if( clearCompositionId          == K_k     ||
		bishopAgnosticCompositionId == KB_k    ||
		bishopAgnosticCompositionId == K_kb    ||
		clearCompositionId          == KN_k    ||
		clearCompositionId          == K_kn    ||
		bishopAgnosticCompositionId == KB_kn   ||
		bishopAgnosticCompositionId == KN_kb   ||
		clearCompositionId          == KN_kn   ||
		clearCompositionId          == KNN_k   ||
		clearCompositionId          == K_knn   ||
		clearCompositionId          == KdB_kdb ||
		clearCompositionId          == KlB_klb ||
		clearCompositionId          == KdBdB_k ||
		clearCompositionId          == K_kdbdb ||
		clearCompositionId          == KlBlB_k ||
		clearCompositionId          == K_klblb    )
	{
		set_insuficient();
	} else {
		clear_insuficient();
	}
}