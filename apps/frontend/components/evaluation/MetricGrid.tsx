import ScoreCard from "./ScoreCard";


type Props = {
    summary: {
        total: number;
        passed: number;
        failed: number;
        score: number;
    };
};


export default function MetricGrid({
    summary
}: Props) {


    const metrics = [

        {
            title:"Overall Score",
            value:`${Math.round(summary.score * 100)}%`,
            subtitle:`${summary.passed}/${summary.total} passed`
        },


        {
            title:"Executions",
            value:`${summary.total}`,
            subtitle:`${summary.failed} failed`
        },


        {
            title:"Pass Rate",
            value:`${Math.round(
                (summary.passed / summary.total) * 100
            )}%`,
        },


        {
            title:"Evaluation Status",
            value:
                summary.failed === 0
                ? "Healthy"
                : "Issues"
        }

    ];


    return (

        <div
            className="
            grid
            gap-4
            grid-cols-1
            md:grid-cols-2
            xl:grid-cols-4
            "
        >

            {
                metrics.map(metric=>(

                    <ScoreCard

                        key={metric.title}

                        title={metric.title}

                        value={metric.value}

                        subtitle={metric.subtitle}

                    />

                ))
            }


        </div>

    );

}