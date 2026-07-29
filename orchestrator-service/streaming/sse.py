import json


class StreamEmitter:

    def metadata(self, metadata: dict):
        return f"data: {json.dumps(metadata)}\n\n"

    def trace(self, step: dict):
        return f"data: {json.dumps(step)}\n\n"

    def token(self, token: str):
        return f"data: {json.dumps({
            'type': 'token',
            'token': token
        })}\n\n"

    def done(self, latency_ms: int):
        return f"data: {json.dumps({
            'type': 'done',
            'latency_ms': latency_ms
        })}\n\n"