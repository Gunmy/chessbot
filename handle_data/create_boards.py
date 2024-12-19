# https://python-chess.readthedocs.io/en/latest/
import csv
import random
import chess
import re
import os
import numpy as np
from tqdm import tqdm
from file_handler import get_offset, save_offset, read_lines

OFFSET_FILE = "handle_data/offset.txt"
CHUNK_SIZE = 3000

BLACK_PIECES = "rnbqkp"
WHITE_PIECES = "RNBQKP"
PIECES = BLACK_PIECES + WHITE_PIECES

MAX_ADVANTAGE = 45
MATE_DISTANCE = 5

EARLY_MOVES = 3
KEEP_EARLY_MOVES = 300
CHANCE_TO_KEEP_EARLY_MOVE = [0.33, 0.16]

OUTPUT_FILE_TRAINING = "training.csv"
OUTPUT_FILE_TESTS = "test.csv"
INPUT_FILE = "handle_data/filtered_games.pgn"

APPEND_TO_TEST_CHANCE = 15

HEADER = ["fen_position", "metadata", "position", "eval"]

def charInString(char, string):
    if char in string:
        return 1
    return 0

def formatEval(eval):
    if isinstance(eval, float):
        if eval >= 0:
            return min(eval, MAX_ADVANTAGE) 
        return max(eval, -MAX_ADVANTAGE)
    if eval[1] == "-":
        return -MAX_ADVANTAGE - MATE_DISTANCE
    return MAX_ADVANTAGE + MATE_DISTANCE


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

def extractInfoFromBoard(board, move):
    fen_position = board.fen()

    extracted_info = fen_position.split()[1:3]

    metadata = [charInString("w", extracted_info[0]), #Turn
            charInString("K", extracted_info[1]), #Castling
            charInString("Q", extracted_info[1]),
            charInString("k", extracted_info[1]),
            charInString("q", extracted_info[1]),]

    eval = formatEval(move[1])

    position = formatPosition(fen_position)

    return [fen_position, metadata, position, eval]

def turnIntoBoards(moves, training_positions, test_positions, offset):
    pattern = r"([a-hRNBQKO0-9O\-x+#=]+[QRBN]?)[?!]* { \[%eval ([#\d\.-]+)\] }"

    parsed_moves = re.findall(pattern, moves)

    result_moves = [
        (move, eval_ if eval_.startswith("#") else float(eval_))
        for move, eval_ in parsed_moves
    ]

    board = chess.Board()

    for i in range(len(result_moves[:EARLY_MOVES])):
        move = result_moves[i]
        
        board.push_san(move[0])

        # Avoid saving too many early-move games
        rdm_num = random.random()
        if ((offset < KEEP_EARLY_MOVES*i) or (offset < KEEP_EARLY_MOVES*2*i and rdm_num <= CHANCE_TO_KEEP_EARLY_MOVE[0]/(EARLY_MOVES-i)) or (offset < KEEP_EARLY_MOVES*3*i and rdm_num <= CHANCE_TO_KEEP_EARLY_MOVE[1]/(EARLY_MOVES-i))):            
            if offset % APPEND_TO_TEST_CHANCE == 0:
                test_positions.append(extractInfoFromBoard(board, move))
            else:
                training_positions.append(extractInfoFromBoard(board, move))


    for move in result_moves[EARLY_MOVES:]:
        board.push_san(move[0])
        if offset % APPEND_TO_TEST_CHANCE == 0:
            test_positions.append(extractInfoFromBoard(board, move))
        else:
            training_positions.append(extractInfoFromBoard(board, move))    

def append_to_csv(data, file_path):
    file_exists = os.path.exists(file_path)

    with open(file_path, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
    
        if not file_exists:
            writer.writerow(HEADER)
        
        for position in data:
            writer.writerow(position)

def create_boards_from_moves(games, OUTPUT_FILE_TRAINING, OUTPUT_FILE_TESTS, offset):

    training_positions = []
    test_positions = []

    i = offset

    for game in tqdm(games):
        turnIntoBoards(game, training_positions, test_positions, i)
        i+= 1

    append_to_csv(training_positions, OUTPUT_FILE_TRAINING)
    print(f"Training data has been written to {OUTPUT_FILE_TRAINING}")

    append_to_csv(test_positions, OUTPUT_FILE_TESTS)
    print(f"Test data has been written to {OUTPUT_FILE_TESTS}")


def main():
    current_offset = get_offset(OFFSET_FILE)

    print(f"Reading games {current_offset + 1} to {current_offset + CHUNK_SIZE}...")

    games = read_lines(INPUT_FILE, current_offset, CHUNK_SIZE)

    create_boards_from_moves(games, OUTPUT_FILE_TRAINING, OUTPUT_FILE_TESTS, current_offset)

    if len(games) < CHUNK_SIZE:
        print("End of file reached.")
        save_offset(0, OFFSET_FILE)

    else:
        save_offset(current_offset + CHUNK_SIZE, OFFSET_FILE)

if __name__ == "__main__":
    main()

