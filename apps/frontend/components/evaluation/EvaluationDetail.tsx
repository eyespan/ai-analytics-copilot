import type {
    EvaluationResult
} from "@/lib/evaluation";


function parseJson(value: unknown) {

    if (!value) {
        return {};
    }


    if (typeof value === "string") {

        try {
            return JSON.parse(value);
        }
        catch {

            return {};

        }

    }


    return value;

}

export default function EvaluationDetail({

    result

}: {

    result: EvaluationResult;

}) {


    
    const diff = parseJson(result.diff);
    
    const replay = parseJson(result.replay);
    
    const trace = parseJson(result.trace);  



    return (

        <div
            className="
                border
                rounded-xl
                p-6
                space-y-6
                bg-zinc-950
                text-white
            "
        >

            <h2 className="text-xl font-bold text-white">
                Evaluation Detail
            </h2>



            <section>

                <h3 className="font-semibold text-zinc-200">
                    Score
                </h3>


                <div className="text-3xl font-bold">

                    {Math.round(result.score * 100)}%

                </div>

            </section>




            <section>

                <h3 className="font-semibold text-zinc-200">
                    Score Breakdown
                </h3>


                <div className="space-y-2">


                    <div>
                        Alignment:
                        {" "}
                        {Math.round(
                            result.alignment_score * 100
                        )}%
                    </div>


                    <div>
                        Coverage:
                        {" "}
                        {Math.round(
                            result.coverage_score * 100
                        )}%
                    </div>


                    <div>
                        Ordering:
                        {" "}
                        {Math.round(
                            result.ordering_score * 100
                        )}%
                    </div>


                    <div>
                        Penalty:
                        {" "}
                        {result.penalty_score}
                    </div>


                </div>


            </section>




            <section>

                <h3 className="font-semibold text-zinc-200">
                    Diff
                </h3>


                <pre
                    className="
                        bg-zinc-900
                        text-white
                        p-4
                        rounded-lg
                        overflow-x-auto
                        text-sm
                        leading-relaxed
                    "
                >

                    {JSON.stringify(
                        diff,
                        null,
                        2
                    )}

                </pre>


            </section>




            <section>

                <h3 className="font-semibold text-zinc-200">
                    Replay
                </h3>


                <pre
                    className="
                        bg-zinc-900
                        text-white
                        p-4
                        rounded-lg
                        overflow-x-auto
                        text-sm
                        leading-relaxed
                    "
                >

                    {JSON.stringify(
                        replay,
                        null,
                        2
                    )}

                </pre>


            </section>




            <section>

                <h3 className="font-semibold text-zinc-200">
                    Execution Trace
                </h3>


                <pre
                    className="
                        bg-zinc-900
                        text-white
                        p-4
                        rounded-lg
                        overflow-x-auto
                        text-sm
                        leading-relaxed
                    "
                >

                    {JSON.stringify(
                        trace.steps ?? [],
                        null,
                        2
                    )}

                </pre>


            </section>




            <section>

                <h3 className="font-semibold text-zinc-200">
                    Metadata
                </h3>


                <div className="text-sm space-y-1">


                    <div>
                        Dataset:
                        {" "}
                        {result.dataset_id}
                    </div>


                    <div>
                        Latency:
                        {" "}
                        {result.latency_ms} ms
                    </div>


                    <div>
                        Created:
                        {" "}
                        {result.created_at}
                    </div>


                </div>


            </section>


        </div>

    );

}