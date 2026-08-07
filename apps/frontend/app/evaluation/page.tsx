"use client";

import { useEffect, useState } from "react";

import MetricGrid from "@/components/evaluation/MetricGrid";
import EvaluationTable from "@/components/evaluation/EvaluationTable";
import EvaluationDetail from "@/components/evaluation/EvaluationDetail";

import type {
    EvaluationResponse,
    EvaluationResult
} from "@/lib/evaluation";



export default function EvaluationPage() {


    const [data,setData] =
        useState<EvaluationResponse | null>(null);


    const [selected,setSelected] =
        useState<EvaluationResult | null>(null);



    useEffect(()=>{


        async function loadEvaluation(){


            const response =
            await fetch(
                "/api/evaluations",
                {
                    cache:"no-store"
                }
            );


        
            const result = await response.json();

            console.log("Evaluation API response:", result);

            if (
    result &&
    result.summary &&
    result.results
) {

    setData(result);

}
else {

    console.error(
        "Invalid evaluation response",
        result
    );

}

        }


        loadEvaluation();


    },[]);



    if(!data){

        return (
            <main className="p-6">
                Loading evaluation...
            </main>
        );

    }



    return (

        <main className="p-6">


            <h1 className="text-3xl font-bold mb-8">
                Evaluation Dashboard
            </h1>



            <MetricGrid

                summary={data.summary}

            />



            <div className="mt-8">


                <EvaluationTable

                    results={data.results}

                    onSelect={setSelected}

                />


            </div>



            {
                selected &&

                <div className="mt-8">

                    <EvaluationDetail

                        result={selected}

                    />

                </div>

            }


        </main>

    );

}