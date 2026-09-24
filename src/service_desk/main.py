from fastapi import FastAPI

app = FastAPI(title="Service Desk Copilot")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
