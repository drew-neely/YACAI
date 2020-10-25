# Create your views here.
from django.shortcuts import render
from django.shortcuts import redirect
from chessAI.forms import UpdateBoardForm
import chess
import chess.svg
board = chess.Board()

# Create your views here.
def index(request):
    global board
    """View function for home page of site."""

    if request.method == 'POST':
        form = UpdateBoardForm(request.POST)
        if form.is_valid():
            move = form.cleaned_data['move']
            reset = form.cleaned_data['reset']
            print(move)
            print(reset)
            if reset == 'resetBoard':
                board = chess.Board()
            else:
                board.push_san(move)
        else:
            print("form aint valid bucko")
    else:
        form = UpdateBoardForm()
        board = chess.Board()
    
    #squares = board.attacks(chess.E4)
    chess_svg = chess.svg.board(board, size=600)
    context = {
        'form': form,
        'chess_board': board,
        'chess_svg': chess_svg
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)
