"use client";

//import type { StreamEvent } from "@/hooks/useAskStream";

import { StreamMetadata } from "@/hooks/useAskStream";


type Props = {
    metadata: StreamMetadata | null;
    latency: number | null;
};


export default function MetadataCard({
    metadata,
    latency
}: Props){

    if(!metadata){
        return null;
    }


    return (
        <div>

            <h3>
                Execution Metadata
            </h3>

            <p>
                Provider: {metadata.provider}
            </p>

            <p>
                Model: {metadata.model}
            </p>

            <p>
                Complexity: {metadata.complexity}
            </p>

            <p>
                Reason: {metadata.reason}
            </p>

            <p>
                Latency: {
                    latency
                    ? `${latency} ms`
                    : "-"
                }
            </p>

        </div>
    );
}