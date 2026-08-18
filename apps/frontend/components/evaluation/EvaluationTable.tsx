import type {
    EvaluationResult
} from "@/lib/evaluation";


export default function EvaluationTable({

    results,

    onSelect

}:{

    results: EvaluationResult[];

    onSelect:(r: EvaluationResult)=>void;

}) {


    return (

        <div className="overflow-x-auto">

            <table className="w-full border-collapse">


                <thead>

                    <tr className="border-b">

                        <th className="p-3 text-left">
                            Dataset
                        </th>

                        <th className="p-3 text-left">
                            Query
                        </th>

                        <th className="p-3 text-left">
                            Score
                        </th>

                        <th className="p-3 text-left">
                            Latency
                        </th>

                        <th className="p-3 text-left">
                            Status
                        </th>

                        <th className="p-3 text-left">
                            Created
                        </th>

                    </tr>

                </thead>



                <tbody>


                {
                    results.map(result => (

                        <tr

                            key={result.evaluation_id}

                            onClick={() => onSelect(result)}

                            className="
                                cursor-pointer
                                border-b
                                hover:bg-zinc-800
                            "

                        >

                            <td className="p-3">
                                {result.dataset_id}
                            </td>


                            <td className="p-3">
                                {result.query}
                            </td>


                            <td className="p-3">
                                {Math.round(result.score * 100)}%
                            </td>


                            <td className="p-3">
                                {result.latency_ms} ms
                            </td>


                            <td className="p-3">

                                {
                                    result.passed
                                    ?
                                    "PASS"
                                    :
                                    "FAIL"
                                }

                            </td>


                            <td className="p-3">
                                {result.created_at}
                            </td>


                        </tr>

                    ))
                }


                </tbody>


            </table>


        </div>

    );

}