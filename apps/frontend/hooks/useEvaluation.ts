"use client";

export type EvaluationRun = {
    query: string;
    score: number;
    latency_ms: number;
    passed: boolean;
};

export function useEvaluation() {

    async function evaluate(dataset: unknown) {

        const response = await fetch(
            "/api/evaluate",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    dataset,
                }),
            }
        );

        if (!response.ok) {

            throw new Error("Evaluation failed");

        }

        return response.json();

    }

    return {
        evaluate,
    };

}