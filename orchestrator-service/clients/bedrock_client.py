# clients/bedrock_client.py

import json

import boto3
from config.settings import AWS_REGION


class BedrockClient:

    def __init__(self, model_id: str):

        self.model_id = model_id

        self.client = boto3.client("bedrock-runtime", region_name=AWS_REGION)

    # -------------------------------------------------
    # NON-STREAMING
    # -------------------------------------------------

    def generate(self, prompt: str) -> str:

        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 2048,
            "messages": [{"role": "user", "content": prompt}],
        }

        response = self.client.invoke_model(
            modelId=self.model_id,
            body=json.dumps(body),
            contentType="application/json",
            accept="application/json",
        )

        payload = json.loads(response["body"].read())

        content = payload.get("content", [])

        if not content:
            return ""

        return content[0].get("text", "")

    # -------------------------------------------------
    # STREAMING
    # -------------------------------------------------

    def stream_generate(self, prompt: str):

        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 2048,
            "messages": [{"role": "user", "content": prompt}],
        }

        response = self.client.invoke_model_with_response_stream(
            modelId=self.model_id,
            body=json.dumps(body),
            contentType="application/json",
            accept="application/json",
        )

        stream = response["body"]

        for event in stream:

            chunk = event.get("chunk")

            if not chunk:
                continue

            try:

                data = json.loads(chunk["bytes"].decode("utf-8"))

                if data.get("type") == "content_block_delta":
                    yield data["delta"].get("text", "")

            except Exception:
                continue
