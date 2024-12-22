import { useEffect, useState } from "react";
import { Chess } from "chess.js";
import { Chessboard } from "react-chessboard";
import { Flex, Paper, Text } from "@mantine/core";
import axios from "axios";
import ChessArrow from "./ChessArrow";
import stylesheet from './ChessGame.module.css';

interface Dictionary {
  [key: string]: string;
}

export default function ChessGame() {
  const [game, setGame] = useState<Chess>(new Chess()); // Chess.js instance
  const [fen, setFen] = useState<string>(game.fen()); // Current FEN position

  // Use the evaluation hook with the current FEN position

  const [loading, setLoading] = useState<boolean>(false);

  const turnNotation: Dictionary = {
    b: "black",
    w: "white"
  };

  const fetchMove = async (position: string) => {
    try {
      setLoading(true);
      const response = await axios.get("http://localhost:8000/move", {
        params: { position }
      });
      const bestMove = response.data;
      console.log("Best move:", bestMove);
      return bestMove;
    } catch (error) {
      console.error("Error fetching move:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (game.turn() === "b" && !loading && !game.game_over() && !game.in_draw() && game.moves().length !== 0) { //game.turn() === "b" && !loading
      const getMove = async () => {
        const move = await fetchMove(game.fen());
        if (move) {
            safeGameMutate((gameInstance) => {
                gameInstance.move(move);
            });
        }
      };
      getMove();
    }
  }, [fen]);


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
    return true; // Move was successful
  }

  return (
    <Flex
    justify="center"
    align="center"
    style={{ width: '100vw', height: '100vh' }} // Full viewport height
  >
      <Paper shadow="md" p="xl" className={stylesheet.paper} >
        <Flex justify="space-between" align="center" style={{ width: '100%' }}>
          <Text>Status: {game.game_over() ? "over" : "ongoing"}</Text>
          <Text>{game.game_over() ? "Loser:" : "Turn:"} {turnNotation[game.turn()]}</Text>
        </Flex>
        <Chessboard
          position={game.fen()} // Use the game's FEN for the board
          onPieceDrop={onDrop}
          boardWidth={400} // Adjust board size
        />
        <ChessArrow fen={fen}/>
      </Paper>
    </Flex>
  );
}
