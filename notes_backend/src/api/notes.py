from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# SQLite DB configuration
DATABASE_URL = "sqlite:///./notes.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False)
Base = declarative_base()

# SQLAlchemy Note model
class NoteModel(Base):
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

# Pydantic schemas
class NoteCreate(BaseModel):
    title: str = Field(..., description="The title of the note", min_length=1, max_length=200)
    content: str = Field(..., description="The content of the note")

class NoteUpdate(BaseModel):
    title: Optional[str] = Field(None, description="The title of the note", min_length=1, max_length=200)
    content: Optional[str] = Field(None, description="The content of the note")

class NoteOut(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

router = APIRouter(
    prefix="/notes",
    tags=["Notes"]
)

# PUBLIC_INTERFACE
@router.post(
    "",
    response_model=NoteOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new note",
    description="Create a new note with a title and content."
)
def create_note(note: NoteCreate, db: Session = Depends(get_db)):
    """Create and persist a new note."""
    new_note = NoteModel(
        title=note.title,
        content=note.content,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(new_note)
    db.commit()
    db.refresh(new_note)
    return new_note

# PUBLIC_INTERFACE
@router.get(
    "",
    response_model=List[NoteOut],
    summary="List all notes",
    description="Get a list of all notes."
)
def get_notes(db: Session = Depends(get_db)):
    """Retrieve a list of all notes."""
    notes = db.query(NoteModel).all()
    return notes

# PUBLIC_INTERFACE
@router.get(
    "/{note_id}",
    response_model=NoteOut,
    summary="Get a specific note by ID",
    description="Retrieve a note by its ID."
)
def get_note(note_id: int, db: Session = Depends(get_db)):
    """Get details of a specific note by ID."""
    note = db.query(NoteModel).filter_by(id=note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

# PUBLIC_INTERFACE
@router.put(
    "/{note_id}",
    response_model=NoteOut,
    summary="Update a note by ID",
    description="Update the title and/or content of a note."
)
def update_note(note_id: int, note_update: NoteUpdate, db: Session = Depends(get_db)):
    """Update an existing note's title and/or content."""
    note = db.query(NoteModel).filter_by(id=note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    if note_update.title is not None:
        note.title = note_update.title
    if note_update.content is not None:
        note.content = note_update.content
    note.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(note)
    return note

# PUBLIC_INTERFACE
@router.delete(
    "/{note_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a note by ID",
    description="Delete a note specified by its ID."
)
def delete_note(note_id: int, db: Session = Depends(get_db)):
    """Delete a note given its ID."""
    note = db.query(NoteModel).filter_by(id=note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    db.delete(note)
    db.commit()
    return None
