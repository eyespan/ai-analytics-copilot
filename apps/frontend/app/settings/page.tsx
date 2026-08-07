"use client";


import { useState } from "react";

import type {
    Settings
} from "@/lib/settings";


const defaultSettings:Settings = {

    model:{
        provider:"ollama",
        model:"qwen2.5:3b",
        fallback:false
    },


    agent:{
        max_steps:5,
        planner_enabled:true,
        repair_enabled:true
    },


    guardrails:{
        prompt_injection:true,
        tool_validation:true,
        output_validation:true
    },


    evaluation:{
        auto_run:true,
        store_traces:true,
        retention_days:30
    }

};



export default function SettingsPage(){


const [settings,setSettings] =
    useState(defaultSettings);



function update(
    section:keyof Settings,
    key:string,
    value:any
){

    setSettings({

        ...settings,

        [section]:{

            ...settings[section],

            [key]:value

        }

    });

}



return (

<main className="p-6">


<h1 className="text-3xl font-bold mb-8">
Settings
</h1>



<section className="space-y-6">


<div className="border rounded p-5">

<h2 className="font-semibold mb-4">
Model Configuration
</h2>


<p>
Provider:
<b className="ml-2">
{settings.model.provider}
</b>
</p>


<p>
Model:
<b className="ml-2">
{settings.model.model}
</b>
</p>


</div>



<div className="border rounded p-5">

<h2 className="font-semibold mb-4">
Agent Configuration
</h2>


<label>

Max Steps

<input

className="ml-3 border p-1"

type="number"

value={
settings.agent.max_steps
}

onChange={
e =>
update(
"agent",
"max_steps",
Number(e.target.value)
)
}

/>

</label>


</div>



<div className="border rounded p-5">


<h2 className="font-semibold mb-4">
Guardrails
</h2>


{
Object.entries(
settings.guardrails
)
.map(
([key,value])=>(

<label
key={key}
className="block"
>

<input

type="checkbox"

checked={value}

onChange={
e =>
update(
"guardrails",
key,
e.target.checked
)
}

/>

<span className="ml-2">
{key}
</span>


</label>

))
}


</div>



<div className="border rounded p-5">

<h2 className="font-semibold mb-4">
Evaluation
</h2>


<label>

Retention Days

<input

className="ml-3 border p-1"

type="number"

value={
settings.evaluation.retention_days
}

onChange={
e =>
update(
"evaluation",
"retention_days",
Number(e.target.value)
)
}

/>

</label>


</div>



<button

className="
mt-6
px-4
py-2
rounded
bg-blue-600
text-white
"

onClick={()=>{

console.log(settings)

}}

>

Save Changes

</button>


</section>


</main>

);

}