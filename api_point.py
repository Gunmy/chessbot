from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
from tensorflow.keras.models import load_model
import chess


model = load_model('chess_evaluator.keras')

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Replace with your frontend's origin
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type"],
)

BLACK_PIECES = "rnbqkp"
WHITE_PIECES = "RNBQKP"
PIECES = BLACK_PIECES + WHITE_PIECES

def charInString(char, string):
    if char in string:
        return 1
    return 0

def formatPosition(position):
    rows = position.split("/")
    formattedRows = np.zeros((8, 8, 8))

    for i in range(8):
        j = 0
        n = 0

        while j < 8:
            square = rows[i][n]     

            if square in PIECES:
                if square in BLACK_PIECES:
                    formattedRows[i, j, 0] = 1
                    formattedRows[i, j, BLACK_PIECES.index(square) + 2] = 1
                
                else:
                    formattedRows[i, j, 1] = 1
                    formattedRows[i, j, WHITE_PIECES.index(square) + 2] = 1
                j += 1
            
            else:
                j += int(square)

            n += 1
            
    return formattedRows.tolist()

def extractInfoFromFen(fen):

    extracted_info = fen.split()[1:3]

    metadata = [charInString("w", extracted_info[0]), #Turn
            charInString("K", extracted_info[1]), #Castling
            charInString("Q", extracted_info[1]),
            charInString("k", extracted_info[1]),
            charInString("q", extracted_info[1]),]

    position = formatPosition(fen)
    return position, metadata

def eval(position):

    pos, meta = extractInfoFromFen(position)

    X_board = np.expand_dims(pos, axis=0)
    X_metadata = np.expand_dims(meta, axis=0)

    prediction = model.predict({'board_input': X_board, 'metadata_input': X_metadata})[0, 0]

    return float(prediction)

@app.get("/eval")
async def evaluate(position: str):
    return eval(position)

def min_node(position, depth_left):
    board = chess.Board(position)
    legal_moves = board.legal_moves

    best_evals = []

    for move in legal_moves:
        board = chess.Board(position)
        san_move = board.san(move)
        board.push_san(san_move)

        current_eval = eval(board.fen())

        if len(best_evals) < 3:
            best_evals.append((san_move, current_eval, board.fen()))
        else:
            # Find worst in eval
            index_of_largest = max(enumerate(best_evals), key=lambda x: x[1][1])[0]

            # If worst worse than current, replace it
            if best_evals[index_of_largest][1] > current_eval:
                best_evals[index_of_largest] = (san_move, current_eval, board.fen())

    if len(best_evals) == 0:
        return (0, 500)
    
    if (depth_left == 0):
        index_of_smallest = min(enumerate(best_evals), key=lambda x: x[1][1])[0]
        return best_evals[index_of_smallest]
    
    for i in range(len(best_evals)):
        better_estimate = max_node(best_evals[i][2], depth_left - 1)[1]
        print(better_estimate)
        best_evals[i] = (best_evals[i][0], better_estimate, best_evals[i][2])

    index_of_smallest = min(enumerate(best_evals), key=lambda x: x[1][1])[0]

    print("chose", best_evals[index_of_smallest][1])

    return best_evals[index_of_smallest]


def max_node(position, depth_left):
    board = chess.Board(position)
    legal_moves = board.legal_moves

    best_evals = []

    for move in legal_moves:
        board = chess.Board(position)
        san_move = board.san(move)
        board.push_san(san_move)

        current_eval = eval(board.fen())

        if len(best_evals) < 3:
            best_evals.append((san_move, current_eval, board.fen()))
        else:
            index_of_smallest = min(enumerate(best_evals), key=lambda x: x[1][1])[0]

            if best_evals[index_of_smallest][1] < current_eval:
                best_evals[index_of_smallest] = (san_move, current_eval, board.fen())

    if len(best_evals) == 0:
        return (0, -500)
    
    if (depth_left == 0):
        index_of_largest = max(enumerate(best_evals), key=lambda x: x[1][1])[0]
        return best_evals[index_of_largest]
    
    for i in range(len(best_evals)):
        better_estimate = min_node(best_evals[i][2], depth_left - 1)[1]
        best_evals[i] = (best_evals[i][0], better_estimate, best_evals[i][2])

    index_of_largest = max(enumerate(best_evals), key=lambda x: x[1][1])[0]
    return best_evals[index_of_largest]

@app.get("/move")
async def makeMove(position: str):
    side = position.split()[1]

    print("\n".join(position.split("/")))

    if (side == "b"):
        return min_node(position, 1)[0]
    else:
        return max_node(position, 1)[0]

