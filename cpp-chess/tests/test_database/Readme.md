# About the Game End Test Database

This directory contains hundreds of thousands of real games played on lichess. These games are used primarily to test that cpp-chess engine is able to correctly identify both when a game has ended and also that the game has ended for the correct reason. Using real games to test this instead of randomly generated games has the advantage of providing a diverse set of ending positions arising from a diverse sequence of moves that simple random game generation likely would not have.

The script 'parse_db.py' uses the python-chess engine to parse the pgn files (optionally bz2 compressed) downloaded from the lichess database and calculate for each game what the expected outcome is. It discards games that end in timeout or resignation and also accounts for anomalies (bugs?) that seem to have existed in the lichess engine in and around 2013. This script is very slow, but only needs to be run once per dataset. Run 'python parse_db.py -h' for limited help. The output of this script is a .pgn.list file.

**NOTE:** The Lichess and python-chess engines follow FIDE rules while cpp-chess follows USCF rules. The only major consequence of this is that certain endgames are automatic draw by insuficient material under USCF rules and are not automatic draws under FIDE rules. These endgames are accounted for by the test bench.

The input to the test bench is a .pgn.list file. A .pgn.list file contains a list of games using uci notation and the expected ending reason of the game after the last move given. This data is placed on 3 lines for each game:

	* The first line contains the end reason which may be one of: [checkmate, stalemate, threefold_repetition, fifty_moves, insufficient_material]
	* The second line contains the winner which may be one of: [white, black, draw]
	* The third line contains a space seperated list of the moves of the game in uci notation. Each move is represented in 4 characters, except promotions which are represented in 5.

**NOTE:** For the purpose of saving space in the git repository, the .pgn.list files are bz2 compressed. They must be uncompressed before being used. (with cwd at cpp-chess root run 'bunzip2 -k tests/test_database/*.pgn.list.bz2'). This is not done automatically. 
	TODO: Make the test engine use the compressed files
The original .pgn files from the lichess database are not included in the git repo since they are very large.





*The tests/test_database directory contains data sourced from [database.lichess.org](https://database.lichess.org/) which as of 04-09-2022 is under Creative Commons CC0 1.0 Universal (CC-0) liscence allowing private use, commercial use, modification, and redistribution.*
