"use client";

interface StreamingMessageProps {
  text: string;
}


export default function StreamingMessage({
  text,
}: StreamingMessageProps) {

  return (
    <div className="whitespace-pre-wrap">
      {text}
    </div>
  );
}