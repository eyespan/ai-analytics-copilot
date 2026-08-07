import { NextRequest } from "next/server";

export async function POST(req: NextRequest) {
  const body = await req.text();

  const response = await fetch(`${process.env.ORCHESTRATOR_URL}/evaluate`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body,
  });

  if (!response.ok) {
    return new Response(`Evaluation backend error: ${response.status}`, {
      status: response.status,
    });
  }

  const data = await response.json();
  return Response.json(data);
}

