"use client";


import { useEffect,useState } from "react";

import TraceViewer from "@/components/trace/TraceViewer";

import type {
    TraceResponse,
    Trace
} from "@/lib/trace";


export default function TracesPage(){


const [data,setData] =
    useState<TraceResponse|null>(null);



useEffect(()=>{


async function load(){


const response =
await fetch(
    "/api/traces",
    {
        cache:"no-store"
    }
);


const result =
await response.json();


setData(result);


}


load();


},[]);



if(!data){

return (

<main className="p-6">

Loading traces...

</main>

);

}



return (

<main className="p-6">


<h1 className="text-3xl font-bold mb-8">

Execution Traces

</h1>


{

data.traces.map(trace=>(


<div
key={trace.trace_id}
className="
border
rounded-lg
p-4
mb-6
"
>


<h2 className="font-semibold">

{trace.query}

</h2>


<p className="text-sm text-neutral-500">

{trace.created_at}

</p>


<TraceViewer

steps={trace.steps}

/>


</div>


))

}


</main>

);

}