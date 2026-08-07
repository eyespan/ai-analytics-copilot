"use client";

import type { TraceStep } from "@/lib/trace";

type Props = {
    step: TraceStep;
};

export default function TraceStepView({ step }: Props) {

    return (

        <div
            className="
                border-b
                border-neutral-800
                py-2
                text-sm
            "
        >

            <div className="flex justify-between">

                <span>

                    {step.success ? "✓" : "✗"}{" "}

                    {step.tool}

                </span>

                <span>

                    {step.latency_ms} ms

                </span>

            </div>

            <div
                className="
                    text-xs
                    text-neutral-500
                "
            >
                {step.event_type}
            </div>

        </div>

    );

}