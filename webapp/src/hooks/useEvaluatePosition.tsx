import { useQuery } from "@tanstack/react-query";
import axios from "axios";


/**
 * Hook to fetch the evaluation for a given chess position.
 * @param position The FEN string or position identifier to evaluate.
 */
export const useEvaluation = (position: string) => {
  return useQuery({
    queryKey: ["evaluate", position],
    queryFn: async () => {
      const response = await axios.get<Number>(
        `http://127.0.0.1:8000/eval`,
        {
          params: { position },
        }
      );
      return response.data;
    },
    enabled: !!position, // Prevent the query from running without a position
  });
};
