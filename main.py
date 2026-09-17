from fastapi import FastAPI

from routers.chat import router as chat_router

app = FastAPI(title="Mini Agent")
app.include_router(chat_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
