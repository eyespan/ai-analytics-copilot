import requests
import json

class OllamaClient:
    def __init__(self, base_url: str, model: str):
        self.base_url = base_url
        self.model = model  # store model at init

    def generate(self, prompt: str, stream: bool = False):
        r = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False
            },
            timeout=120
        )
        r.raise_for_status()
        data = r.json()

        if "error" in data:
            raise RuntimeError(data["error"])

        return data

    def stream_generate(self, prompt: str):
        with requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": True
            },
            stream=True,
            timeout=120
        ) as r:
            r.raise_for_status()
            buffer = ""

            for chunk in r.iter_content(chunk_size=1024):
                if not chunk:
                    continue

                buffer += chunk.decode("utf-8", errors="ignore")

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    line = line.strip()

                    if not line:
                        continue

                    try:
                        data = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    if "response" in data:
                        yield data["response"]

                    if data.get("done"):
                        return