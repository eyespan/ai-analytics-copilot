"use client";


import {useState} from "react";


interface Props {
    onSend:(value:string)=>void;
}


export default function ChatInput({
    onSend
}:Props){

    const [input,setInput]=useState("");


    function submit(){

        if(!input.trim())
            return;

        onSend(input);

        setInput("");

    }


    return (

        <div className="flex gap-2 p-4">

            <input
              className="
              flex-1
              border
              rounded
              px-3
              py-2
              "
              value={input}
              onChange={
                e=>setInput(e.target.value)
              }
              placeholder="Ask something..."
            />


            <button
              className="
              px-4
              rounded
              bg-blue-600
              text-white
              "
              onClick={submit}
            >
              Send
            </button>

        </div>

    );
}