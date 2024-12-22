import { useQuery } from "@tanstack/react-query";
import axios from "axios";

/**
 * Hook to fetch the move at the curent position
 * @param position The FEN string or position to get move
 */
export const useMove = (position: string) => {
  return useQuery({
    queryKey: ["move", position],
    queryFn: async () => {
      const response = await axios.get<string>( // Assuming the response is a string (the SAN move)
        `http://127.0.0.1:8000/move`,
        {
          params: { position },
        }
      );
      return response.data;
    },
    enabled: !!position, // Prevent the query from running without a position
  });
};



