# Blunder Buster

Blunder Buster is a human like chess robot. It uses the min-max-algorithm combined with a DNN to calculate what moves to do when. 

The webapp itself also uses the same DNN to evaluate the current position and show what side it thinks is winning.

|![In game](images/ingame.png)|
|:---:|
| A screenshot taken from a game. The robot is black |

# How to run

### Run backend

First you need to install Keras, Tensorflow, chess, and FastAPI. Then run:
```shell
fastapi dev api_point.py
```

### Run frontend

After running the frontend, run:
```shell
cd webapp
npm i
npm run dev
```


# Making the DNN-evaluator

## FEN-position to input

To make it easier for the DNN to learn from the positions, they have to be formatted. 

The standard notation for chess-position is the Forsyth-Edwards Notation (FEN). An example of such a FEN-string is

- r3kb1r/ppp3pp/2bp1q2/4p3/3P4/5N2/PPP2PPP/R1BQR1K1 b kq - 0 10

|![Chess position](images/position.svg)|
|:---:|
| The chess position for the FEN-string |

To keep the network light, I wanted to minimize the amount of inputs. For that reason, the network only gets fed what I find to be the most important parts of the FEN-string; the first 3 words:
- the piece placement (*r3kb1r/ppp3pp...*)
- whos turn it is (*b*)
- and the castling-possibilities (*kq*)

### Formatting the piece placement

The piece-placement is formatted into a 3d-array; (8 x 8 x 8), meaning each square is represented by an array of size 8. 
The first 2 items in the array represents the color of the piece present. 
The rest represent the type of piece.
If there is no piece in the square the array is a zero-array.

### Formatting turn and castling info

The turn and castling information are all formatted into one array of size 5. The first item in the array represents whos turn it is. The other 4 items represent whether white can castle (right and left), and if black can castle (right and left). E.g. if its whites turn and both sides have all their castling opportunities then the array will be [1, 1, 1, 1, 1]

## The network itself

The piece-placement itslef is fed into a deep convolution network, while the metadata is fed into a Fully-Connected-Network (FCN). Then the outputs of the convolution network and the FCN are combined and fed into the same Fully-Connected-Deep Network. The network has 1 output; which is the prediction for the evaluation of the position.

## Training the network

TODO

