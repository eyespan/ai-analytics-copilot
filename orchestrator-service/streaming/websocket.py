from fastapi import WebSocket


class WebSocketHandler:

    async def handle(self, websocket: WebSocket, generator):
        await websocket.accept()

        async for chunk in generator:
            await websocket.send_json({"token": chunk})

        await websocket.close()
