from fastapi import FastAPI

from src.api.v1.endpoints import router

app = FastAPI(title='DPU Application API')


app.include_router(router, prefix='')


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="127.0.0.1", port=8000, reload=True)
