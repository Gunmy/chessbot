import React from "react";
import ReactDOM from "react-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import ChessGame from "./ChessGame";

const queryClient = new QueryClient();

export default function App () {
  return (
    <QueryClientProvider client={queryClient}>
      <ChessGame/>
    </QueryClientProvider>
  );
};
