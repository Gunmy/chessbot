import { useEffect, useState } from "react";
import { Chess } from "chess.js";
import { Chessboard } from "react-chessboard";
import { useEvaluation } from "./hooks/useEvaluatePosition";

export default function ChessGame() {
  const [game, setGame] = useState<Chess>(new Chess()); // Chess.js instance
  const [fen, setFen] = useState<string>(game.fen()); // Current FEN position

  // Use the evaluation hook with the current FEN position
  const { data: evaluation, error, isLoading } = useEvaluation(fen);

  useEffect(() => {
    // Debugging: Log evaluation data whenever it changes
    console.log(evaluation, error, isLoading);
  }, [evaluation, error, isLoading]);

  function safeGameMutate(modify: (gameInstance: Chess) => void) {
    setGame((currentGame: Chess) => {
      const updatedGame = new Chess(currentGame.fen());
      modify(updatedGame);

      // Update the FEN after modifying the game instance
      const newFen = updatedGame.fen();
      setFen(newFen); // Trigger evaluation for the new position

      return updatedGame;
    });
  }

  function makeRandomMove() {
    safeGameMutate((gameInstance) => {
      const possibleMoves = gameInstance.moves();
      if (
        gameInstance.game_over() ||
        gameInstance.in_draw() ||
        possibleMoves.length === 0
      ) {
        return; // Exit if the game is over
      }
      const randomIndex = Math.floor(Math.random() * possibleMoves.length);
      gameInstance.move(possibleMoves[randomIndex]);
    });
  }

  function onDrop(sourceSquare: string, targetSquare: string): boolean {
    let moveMade = false;
    safeGameMutate((gameInstance) => {
      const move = gameInstance.move({
        from: sourceSquare,
        to: targetSquare,
        promotion: "q", // Always promote to queen for simplicity
      });
      moveMade = !!move; // Move is null if it's illegal
    });

    if (!moveMade) return false; // Illegal move
    setTimeout(makeRandomMove, 200); // Make a random move after a short delay
    return true; // Move was successful
  }

  return (
    <div>
      <Chessboard
        position={game.fen()} // Use the game's FEN for the board
        onPieceDrop={onDrop}
        boardWidth={400} // Adjust board size
      />
      {isLoading && <p>Loading evaluation...</p>}
      {error && <p>Error: {error.message}</p>}
      {evaluation !== undefined && <p>Evaluation: {evaluation}</p>}
    </div>
  );
}
