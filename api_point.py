from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
from tensorflow.keras.models import load_model

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

    print(fen, position, metadata)

    return position, metadata

@app.get("/eval")
async def evaluate(position: str):

    pos, meta = extractInfoFromFen(position)

    X_board = np.expand_dims(pos, axis=0)
    X_metadata = np.expand_dims(meta, axis=0)

    prediction = model.predict({'board_input': X_board, 'metadata_input': X_metadata})[0, 0]

    print(prediction)

    return float(prediction)


