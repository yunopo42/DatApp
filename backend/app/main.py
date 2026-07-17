from fastapi import FastAPI

app = FastAPI(title='DatApp API')

@app.get("/health" , tags=["health"])
def health_check() -> dict[str , str]:
    return {"status" : "ok"}
