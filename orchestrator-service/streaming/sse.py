import json


class StreamEmitter:


    def _encode(self, payload: dict):
        return (
            "data: "
            + json.dumps(payload)
            + "\n\n"
        )


    def metadata(self, data: dict):

        return self._encode({
            "type": "metadata",
            **data,
        })


    def token(self, token: str):

        return self._encode({
            "type": "token",
            "token": token,
        })


    def trace(self, trace_data: dict):

        return self._encode({
            "type": "trace",
            **trace_data,
        })


    def done(self, latency_ms: int):

        return self._encode({
            "type": "done",
            "latency_ms": latency_ms,
        })