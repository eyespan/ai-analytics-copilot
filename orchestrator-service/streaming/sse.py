import json


class StreamEmitter:


    def emit_token(self, chunk: str):

        return (
            "data: "
            + json.dumps(
                {
                    "type": "token",
                    "token": chunk,
                }
            )
            + "\n\n"
        )


    def emit_metadata(
        self,
        provider: str,
        model: str,
        route: str,
        latency_ms: int = 0,
    ):

        return (
            "data: "
            + json.dumps(
                {
                    "type": "metadata",
                    "provider": provider,
                    "model": model,
                    "route": route,
                    "latency_ms": latency_ms,
                }
            )
            + "\n\n"
        )