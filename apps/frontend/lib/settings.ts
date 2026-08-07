export type Settings = {

    model: {

        provider:string;

        model:string;

        fallback:boolean;

    };


    agent: {

        max_steps:number;

        planner_enabled:boolean;

        repair_enabled:boolean;

    };


    guardrails: {

        prompt_injection:boolean;

        tool_validation:boolean;

        output_validation:boolean;

    };


    evaluation: {

        auto_run:boolean;

        store_traces:boolean;

        retention_days:number;

    };

};