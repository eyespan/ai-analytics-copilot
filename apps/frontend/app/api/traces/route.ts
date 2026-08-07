import { NextResponse } from "next/server";


export async function GET(){

    const response = await fetch(
        `${process.env.ORCHESTRATOR_URL}/traces`,
        {
            cache:"no-store"
        }
    );


    if(!response.ok){

        return NextResponse.json(
            {
                error:"Trace backend error"
            },
            {
                status:response.status
            }
        );

    }


    const data = await response.json();


    return NextResponse.json(data);

}