import { NextResponse } from "next/server";

export async function GET() {

    const response = await fetch(
        `${process.env.ORCHESTRATOR_URL}/evaluations`,
        {
            cache: "no-store",
        }
    );

    if (!response.ok) {

        const text = await response.text();

        console.error("Evaluation backend:", response.status, text);

        return NextResponse.json(
            {
                status: response.status,
                error: text,
            },
            {
                status: response.status,
            }
        );

    }

    return NextResponse.json(await response.json());

}