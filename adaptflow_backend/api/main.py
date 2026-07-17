from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

from api.routers import exports, health, jobs, progress, sessions

load_dotenv()

app = FastAPI(title="AdaptFlow API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


app.include_router(jobs.router, prefix="/api")
app.include_router(health.router, prefix="/api")
app.include_router(progress.router, prefix="/api")
app.include_router(sessions.router, prefix="/api")
app.include_router(exports.router, prefix="/api")
