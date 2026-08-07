"use client";

import type { TraceStep } from "@/lib/trace";

export type StreamMetadata = {
    type: "metadata";
    provider: string;
    model: string;
    complexity: string;
    reason?: string;
};


export type StreamDone = {
    type: "done";
    latency_ms: number;
};


export type StreamTrace = {
    type: "trace";
    trace: TraceStep;
};


export type StreamEvent =
    | StreamMetadata
    | StreamDone
    | StreamTrace
    | {
        type: "token";
        token: string;
    };

export function useAskStream(){

  
    async function ask(
        query: string,
        onToken: (token: string) => void,
        onMetadata: (metadata: StreamMetadata) => void,
        onTrace: (trace: TraceStep) => void,
        onDone: (done: StreamDone) => void
    ){

        const response = await fetch(
            "/api/ask-stream",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    query,
                    session_id: "frontend"
                })
            }
        );


        if (!response.ok) {

            throw new Error(
                `Streaming request failed: ${response.status}`
            );

        }


        const reader =
            response.body?.getReader();


        if (!reader) {
            return;
        }


        const decoder =
            new TextDecoder();


        let buffer = "";


        while(true){

            const {
                value,
                done
            } = await reader.read();


            if(done)
                break;


            buffer += decoder.decode(
                value,
                {
                    stream: true
                }
            );


            const events =
                buffer.split("\n\n");


            // keep incomplete SSE event
            buffer =
                events.pop() || "";


            for(const event of events){

                if(!event.startsWith("data:"))
                    continue;


                const payload =
                    event
                        .replace(
                            "data:",
                            ""
                        )
                        .trim();


                if(!payload)
                    continue;


                try {

                    const json: StreamEvent =
                        JSON.parse(payload);


                    if(json.type === "metadata"){

                        onMetadata(json);

                    }


                    if(json.type === "token"){

                        onToken(json.token);
                    
                    }

                    if(json.type==="done"){

                        onDone(json);
                    
                    }

                    if (json.type === "trace") {

                        onTrace(json.trace);
                    
                        continue;
                    
                    }


                } catch(error){

                    console.error(
                        "Failed parsing SSE event:",
                        payload,
                        error
                    );

                }

            }

        }

    }


    return {
        ask
    };

}