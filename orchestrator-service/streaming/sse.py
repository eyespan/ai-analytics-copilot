#from fastapi.responses import StreamingResponse
import json


class StreamEmitter:

    def emit(self, chunk: str):
        return f"data: {json.dumps({'token': chunk})}\n\n"

    #def emit(self, chunk: str):
        #return f"data: {json.dumps({'token': chunk})}\n\n"


    #def sse_response(generator):
        #return StreamingResponse(generator, media_type="text/event-stream")