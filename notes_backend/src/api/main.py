from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.notes import router as notes_router

app = FastAPI(
    title="Notes API",
    description="FastAPI backend for a simple notes taking application.",
    version="1.0.0",
    openapi_tags=[
        {"name": "Notes", "description": "Operations with notes (create, read, update, delete)."},
        {"name": "Health", "description": "Health check endpoint."}
    ]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["Health"])
def health_check():
    """Health check endpoint. Returns a simple status message."""
    return {"message": "Healthy"}

# Register notes router
app.include_router(notes_router)
