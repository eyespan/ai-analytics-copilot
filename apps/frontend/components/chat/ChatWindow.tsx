"use client";

import { useState } from "react";

import ChatInput from "./ChatInput";
import StreamingMessage from "./StreamingMessage";
import MetadataCard from "./MetadataCard";

import { useAskStream } from "@/hooks/useAskStream";
import {
    StreamMetadata
} from "@/hooks/useAskStream";

import TraceViewer from "@/components/trace/TraceViewer";

import type { TraceStep } from "@/lib/trace";


export default function ChatWindow() {

    const [messages, setMessages] =
        useState<string[]>([]);

    const [streaming, setStreaming] =
        useState("");

    const [metadata,setMetadata] =
        useState<StreamMetadata | null>(null);
    
    const [latency, setLatency] =
        useState<number | null>(null);

    const [traceSteps, setTraceSteps] =
        useState<TraceStep[]>([]);


    const { ask } =
        useAskStream();



    async function handleSend(query: string) {

        setMessages(prev => [
            ...prev,
            `You: ${query}`
        ]);


        setStreaming("");

        setMetadata(null);

        setTraceSteps([]);


        await ask(

            query,
        
            (token) => {
        
                setStreaming(
                    previous => previous + token
                );
        
            },
        
            (metadata) => {
        
                setMetadata(metadata);
        
            },
        
            (trace) => {
        
                setTraceSteps(
                    previous => [
                        ...previous,
                        trace
                    ]
                );
        
            },
        
            (done) => {
        
                setLatency(done.latency_ms);
        
            }
        
        );

    }



    return (
        <div className="flex flex-col h-full">


            <div className="
                flex-1
                overflow-y-auto
                p-6
            ">


                {messages.map(
                    (msg,index)=>(
                        <div key={index}>
                            {msg}
                        </div>
                    )
                )}



                {
                    streaming &&
                    <StreamingMessage
                        text={streaming}
                    />
                }



                {
                    metadata &&
                    <MetadataCard
                        metadata={metadata}
                        latency={latency}
                    />
                }

                <TraceViewer
                    steps={traceSteps}
                />


            </div>



            <ChatInput
                onSend={handleSend}
            />


        </div>
    );
}