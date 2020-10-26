# Create your views here.
from django.shortcuts import render
from django.shortcuts import redirect
from chessAI.forms import UpdateBoardForm
from django.http import HttpResponse
import speech_recognition as sr
import librosa
import soundfile as sf
from chessAI.AI_player import AI_Player
import subprocess
import chess
import chess.svg
import ffmpeg
import time
board = chess.Board()
player = AI_Player()

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
                print(board.legal_moves)
                board.push_san(move)
                if not board.is_game_over():
                    board.push(player.get_move(board, chess.BLACK))
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

def test(request):

    return render(request, 'test.html')

def voice_request(request):
    global board
    if request.method == 'POST':
        print("rescievedRequest")
        #print(request.body)
        f = open('./file.wav', 'wb')
        f.write(request.body)
        f.close()
        #command = ['ffmpeg', '-y', '-i', './file.webm', '-c:a', 'pcm_f32le', './out.wav']
        #subprocess.run(command,stdout=subprocess.PIPE,stdin=subprocess.PIPE)
        r = sr.Recognizer()
        x,_ = librosa.load('./file.wav', sr=16000)
        sf.write('tmp.wav', x, 16000)
        time.sleep(1)
        soundM = sr.AudioFile("./tmp.wav")
        with soundM as source:
            audio = r.record(source)
        move = r.recognize_google(audio)
        print(" I heard:  ", move)
        board.push_san(move.lower())
        board.push(player.get_move(board, chess.BLACK))
        print(board)
    else:
        print("get Request")
        form = UpdateBoardForm()
        board = chess.Board()
    #board.push(player.get_move(board, chess.BLACK))
    form = UpdateBoardForm()
    chess_svg = chess.svg.board(board, size=600)
    context = {
        'form': form,
        'chess_board': board,
        'chess_svg': chess_svg
    }
    return HttpResponse(chess_svg, content_type='image/vnd.ms-excel')
