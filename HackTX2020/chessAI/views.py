from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
import chess
import chess.svg
board = chess.Board()

# Create your views here.
def index(request):
    """View function for home page of site."""

    
    
    #squares = board.attacks(chess.E4)
    chess_svg = chess.svg.board(board, size=600)
    context = {
        'chess_board': board,
        'chess_svg': chess_svg
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)

def updateBoard (request, move):
    """View function for home page of site."""

    
    
    #squares = board.attacks(chess.E4)
    chess_svg = chess.svg.board(board, size=600)
    context = {
        'chess_board': board,
        'chess_svg': chess_svg
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)