from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from app.routers import tables, data, export, storage
import uvicorn

app = FastAPI(
    title="DataForge API",
    description="Generate and manage structured/unstructured data for any table",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.include_router(tables.router, prefix="/api/tables", tags=["Tables"])
app.include_router(data.router, prefix="/api/data", tags=["Data"])
app.include_router(export.router, prefix="/api/export", tags=["Export"])
app.include_router(storage.router, prefix="/api/storage", tags=["Storage"])


@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
async def health():
    return {"status": "ok", "service": "DataForge"}


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)