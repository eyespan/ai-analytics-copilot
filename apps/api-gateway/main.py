from fastapi import FastAPI

app = FastAPI(title="API Gateway")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
def root():
    return {"message": "API Gateway Running"}
