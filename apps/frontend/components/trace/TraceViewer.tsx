"use client";

import type { TraceStep } from "@/lib/trace";

import TraceStepView from "./TraceStep";

type Props = {

    steps: TraceStep[];

};

export default function TraceViewer({

    steps

}: Props) {

    return (

        <div
            className="
                rounded-lg
                border
                p-4
                mt-4
            "
        >

            <h2
                className="
                    font-semibold
                    mb-3
                "
            >
                Execution Trace
            </h2>

            {

                steps.length === 0

                ? (

                    <p className="text-sm text-neutral-500">

                        Waiting for execution...

                    </p>

                )

                : (

                    steps.map(

                        step => (

                            <TraceStepView

                                key={`${step.step}-${step.tool}`}

                                step={step}

                            />

                        )

                    )

                )

            }

        </div>

    );

}