export type TraceStep = {

    step: number | string;

    tool:string;

    event_type:string;

    success:boolean;

    latency_ms:number;

    args?:unknown;

    output?:unknown;

};


export type Trace = {

    trace_id:string;

    query:string;

    steps:TraceStep[];

    latency_ms:number;

    created_at:string;

};


export type TraceResponse = {

    traces:Trace[];

};