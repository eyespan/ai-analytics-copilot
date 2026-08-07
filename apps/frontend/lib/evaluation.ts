export type EvaluationSummary = {
    total: number;
    passed: number;
    failed: number;
    score: number;
};


export type EvaluationResult = {

    evaluation_id: string;

    dataset_id: string;

    query: string;

    passed: boolean;

    score: number;


    alignment_score: number;

    coverage_score: number;

    ordering_score: number;

    penalty_score: number;


    latency_ms: number;


    diff:{
        missing:string[];
        extra:string[];
        mismatches:unknown[];
    };


    replay:{
        deterministic:boolean;
        trace_match:boolean;
        divergence_points:unknown[];
    };


    trace:{
        trace_id:string;
        query:string;
        steps:unknown[];
    };


    created_at: string;

};


export type EvaluationResponse = {

    summary: EvaluationSummary;

    results: EvaluationResult[];

};