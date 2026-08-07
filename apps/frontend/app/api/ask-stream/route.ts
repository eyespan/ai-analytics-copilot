import { NextRequest } from "next/server";

export async function POST(req: NextRequest) {
  console.log("ORCHESTRATOR_URL =", process.env.ORCHESTRATOR_URL);
  const body = await req.text();

  const response = await fetch(
    `${process.env.ORCHESTRATOR_URL}/ask-stream`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body,
    }
  );

  if (!response.ok) {
    return new Response(
      `Backend error: ${response.status}`,
      { status: response.status }
    );
  }

  return new Response(response.body, {
    status: response.status,
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache",
      Connection: "keep-alive",
    },
  });
}


