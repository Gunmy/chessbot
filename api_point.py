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

def min_node(position, depth_left, branch_factor):
    board = chess.Board(position)
    legal_moves = board.legal_moves

    positions = []
    metadatas = []
    move_datas = []

    for move in legal_moves:
        board = chess.Board(position)
        san_move = board.san(move)
        board.push_san(san_move)

        current_pos, current_meta = extractInfoFromFen(board.fen())

        positions.append(current_pos)
        metadatas.append(current_meta)
        move_datas.append((san_move, board.fen()))

    if len(positions) == 0:
        return (0, 0, 500)

    predictions = np.ravel(model.predict({'board_input': np.array(positions), 'metadata_input': np.array(metadatas)}))
    
    if (depth_left == 0):
        min_index = np.argmin(predictions)
        return (move_datas[min_index][0], move_datas[min_index][1], predictions[min_index])

    min_index = np.argmin(predictions)
    bottom_indexes = np.argsort(predictions)[:branch_factor]

    index = bottom_indexes[0]
    better_estimate = max_node(move_datas[index][1], depth_left - 1, branch_factor - 1)[2]

    best_option = (move_datas[index][0], move_datas[index][1], better_estimate)
    for index in bottom_indexes[1:]:
        better_estimate = max_node(move_datas[index][1], depth_left - 1, branch_factor - 1)[2]
        if better_estimate < best_option[2]:
            best_option = (move_datas[index][0], move_datas[index][1], better_estimate)
    
    return best_option


def max_node(position, depth_left, branch_factor):
    board = chess.Board(position)
    legal_moves = board.legal_moves

    positions = []
    metadatas = []
    move_datas = []

    for move in legal_moves:
        board = chess.Board(position)
        san_move = board.san(move)
        board.push_san(san_move)

        current_pos, current_meta = extractInfoFromFen(board.fen())

        positions.append(current_pos)
        metadatas.append(current_meta)
        move_datas.append((san_move, board.fen()))

    if len(positions) == 0:
        return (0, 0, -500)

    predictions = np.ravel(model.predict({'board_input': np.array(positions), 'metadata_input': np.array(metadatas)}))
    
    if (depth_left == 0):
        max_index = np.argmax(predictions)
        return (move_datas[max_index][0], move_datas[max_index][1], predictions[max_index])

    top_indexes = np.argsort(predictions)[-branch_factor:][::-1]

    index = top_indexes[0]
    better_estimate = min_node(move_datas[index][1], depth_left - 1, branch_factor - 1)[2]
    best_option = (move_datas[index][0], move_datas[index][1], better_estimate)
    for index in top_indexes[1:]:
        better_estimate = min_node(move_datas[index][1], depth_left - 1, branch_factor - 1)[2]
        if better_estimate > best_option[2]:
            best_option = (move_datas[index][0], move_datas[index][1], better_estimate)

    return best_option

@app.get("/move")
async def makeMove(position: str):
    side = position.split()[1]

    print("\n".join(position.split("/")))

    if (side == "b"):
        return min_node(position, 3, 5)[0]
    else:
        return max_node(position, 3, 5)[0]

