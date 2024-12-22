import { Progress } from "@mantine/core";
import { useEffect, useState } from "react";
import { useEvaluation } from "./hooks/useEvaluation";

interface ChessArrowProps {
    fen: string;
  }
  
export default function ChessArrow({ fen }: ChessArrowProps) {

    const [evaluation, setEval] = useState<number>(50);
    const { data } = useEvaluation(fen);
    useEffect(() => {
        console.log(data);
        if (data) {
            if (data > 50)
                setEval(50)
            else if (data < -50)
                setEval(-50)
            else
                setEval(data)
        }
      }, [data]);


    return (
        <Progress.Root size="xl" radius="0" >
        <Progress.Section color="#B58863" value={50 - Math.sign(evaluation) * Math.sqrt(Math.abs(evaluation))/Math.sqrt(50)*50}>
            <Progress.Label>{(-evaluation).toFixed(2)}</Progress.Label>
        </Progress.Section>
        <Progress.Section color="#F0D9B5" value={50 + Math.sign(evaluation) * Math.sqrt(Math.abs(evaluation))/Math.sqrt(50)*50}>
            <Progress.Label styles={{label: {color: 'black'}}}>{evaluation.toFixed(2)}</Progress.Label>
        </Progress.Section>
        </Progress.Root>
    );
}