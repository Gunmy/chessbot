import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import ChessGame from "./ChessGame";
import { MantineProvider } from '@mantine/core';
import '@mantine/core/styles.css';

const queryClient = new QueryClient();

export default function App () {
  return (
    <MantineProvider>
      <QueryClientProvider client={queryClient}>
          <ChessGame/>
      </QueryClientProvider>
    </MantineProvider>
  );
};
