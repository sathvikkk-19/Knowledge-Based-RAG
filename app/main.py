from fastapi import FastAPI

app = FastAPI(title="Knowledge Graph RAG API")


@app.get("/")
def root():
    return {
        "message": "Knowledge Graph RAG API is running"
    }
