"""Quick sanity tests and timing comparison for the C++ chess engine wrapper.

The script plays random self-play games, checking after each move (and during
the undo walk-back) that the C++ board stays in sync with ``python-chess``.
It also records the time spent in C++ vs. python-chess operations, reporting a
summary when the run completes.
"""

from __future__ import annotations

import argparse
import random
from dataclasses import dataclass
from time import perf_counter
from typing import Iterable, List

from chess import Board as PyBoard
from chess import Move

from cpp_chess import Board


@dataclass
class FenMismatch(Exception):
	fen_cpp: str
	fen_py: str
	move_history: Iterable[Move]

	def __str__(self) -> str:
		move_list = " ".join(move.uci() for move in self.move_history)
		return (
			"FEN mismatch detected.\n"
			f"cpp-chess:    {self.fen_cpp}\n"
			f"python-chess: {self.fen_py}\n"
			f"Move history: {move_list}"
		)


@dataclass
class TimingSummary:
	cpp: float = 0.0
	py: float = 0.0

	def add(self, bucket: str, duration: float) -> None:
		if bucket == "cpp":
			self.cpp += duration
		elif bucket == "py":
			self.py += duration
		else:
			raise ValueError(f"Unknown timing bucket '{bucket}'")


def record_time(summary: TimingSummary, bucket: str, func, *args, **kwargs):
	start = perf_counter()
	try:
		return func(*args, **kwargs)
	finally:
		summary.add(bucket, perf_counter() - start)


def ensure_positions_match(c_board: Board, py_board: PyBoard, history: Iterable[Move], timing: TimingSummary) -> None:
	fen_cpp = c_board.get_fen()
	fen_py = py_board.fen()
	if fen_cpp == fen_py:
		return

	fields_cpp = fen_cpp.split()
	fields_py = fen_py.split()

	if len(fields_cpp) != 6 or len(fields_py) != 6:
		raise FenMismatch(fen_cpp, fen_py, history)

	same_except_ep = all(
		fields_cpp[idx] == fields_py[idx]
		for idx in (0, 1, 2, 4, 5)
	)
	ep_only_difference = (
		same_except_ep
		and fields_py[3] == "-"
		and fields_cpp[3] != "-"
		and not py_board.has_legal_en_passant()
	)

	if not ep_only_difference:
		raise FenMismatch(fen_cpp, fen_py, history)


def play_random_game(game_index: int, timing: TimingSummary) -> int:
	c_board = Board()
	py_board = PyBoard()
	move_history: List[Move] = []

	try:
		while True:
			ensure_positions_match(c_board, py_board, move_history, timing)

			if py_board.is_game_over(claim_draw=True):
				print(f"Game {game_index}: finished after {len(move_history)} moves.")
				break

			legal_moves = list(py_board.legal_moves)
			move = random.choice(legal_moves)
			record_time(timing, "cpp", c_board.make_move, move)
			record_time(timing, "py", py_board.push, move)
			move_history.append(move)

		for move in reversed(move_history):
			record_time(timing, "cpp", c_board.unmake_move)
			record_time(timing, "py", py_board.pop)
			ensure_positions_match(c_board, py_board, move_history, timing)

		return len(move_history)
	finally:
		c_board.free()


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument(
		"--games",
		type=int,
		default=1,
		help="number of random self-play games to run (default: 1)",
	)
	parser.add_argument(
		"--seed",
		type=int,
		help="random seed to make runs deterministic",
	)
	return parser.parse_args()


def main() -> None:
	args = parse_args()

	if args.seed is not None:
		random.seed(args.seed)

	total_moves = 0
	timing = TimingSummary()
	for game_index in range(1, args.games + 1):
		try:
			total_moves += play_random_game(game_index, timing)
		except FenMismatch as mismatch:
			print(mismatch)
			return

	print(f"Total moves across games: {total_moves}")
	ratio_text = f"{timing.py / timing.cpp:.2f}" if timing.py else "n/a"
	print(
		"Timing summary:\n"
		f"  cpp-chess operations   : {timing.cpp:.6f}s\n"
		f"  python-chess operations: {timing.py:.6f}s\n"
		f"  speed ratio (py/cpp)   : {ratio_text}"
	)


if __name__ == "__main__":
	main()
