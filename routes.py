from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Note, Category
from schemas import NoteCreate, NoteResponse, CategoryCreate, CategoryResponse, CategoryUpdate

router = APIRouter()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 📂 CATEGORY ROUTES - COMPLETE CRUD

# Create a Category
@router.post("/categories", response_model=CategoryResponse)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    db_category = db.query(Category).filter(Category.name == category.name).first()
    if db_category:
        raise HTTPException(status_code=400, detail="Category already exists")
    
    new_category = Category(name=category.name)
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category

# Get All Categories
@router.get("/categories", response_model=list[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    return db.query(Category).all()

# Get a Single Category by ID
@router.get("/categories/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

# Update a Category
@router.put("/categories/{category_id}", response_model=CategoryResponse)
def update_category(category_id: int, updated_category: CategoryUpdate, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Check if the new name already exists in another category
    if updated_category.name != category.name:
        existing_category = db.query(Category).filter(Category.name == updated_category.name).first()
        if existing_category:
            raise HTTPException(status_code=400, detail="Category with this name already exists")
    
    category.name = updated_category.name
    db.commit()
    db.refresh(category)
    return category

# Delete a Category
@router.delete("/categories/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db)):
    # First check if the category exists
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Check if there are notes associated with this category
    notes_count = db.query(Note).filter(Note.category_id == category_id).count()
    if notes_count > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot delete category: {notes_count} notes are associated with this category"
        )
    
    # Delete the category
    db.delete(category)
    db.commit()
    return {"message": f"Category '{category.name}' deleted successfully"}

# 📝 NOTE ROUTES

# Create a Note
@router.post("/notes", response_model=NoteResponse)
def create_note(note: NoteCreate, db: Session = Depends(get_db)):
    # Now note.category_id will work correctly with our updated schema
    category = db.query(Category).filter(Category.id == note.category_id).first()
    if not category:
        raise HTTPException(status_code=400, detail="Category does not exist")

    new_note = Note(title=note.title, content=note.content, category_id=note.category_id)
    db.add(new_note)
    db.commit()
    db.refresh(new_note)
    return new_note

# Get All Notes (Including Category Details)
@router.get("/notes", response_model=list[NoteResponse])
def get_notes(db: Session = Depends(get_db)):
    return db.query(Note).all()

# Get a Single Note
@router.get("/notes/{note_id}", response_model=NoteResponse)
def get_note(note_id: int, db: Session = Depends(get_db)):
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

# Update a Note
@router.put("/notes/{note_id}", response_model=NoteResponse)
def update_note(note_id: int, updated_note: NoteCreate, db: Session = Depends(get_db)):
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    category = db.query(Category).filter(Category.id == updated_note.category_id).first()
    if not category:
        raise HTTPException(status_code=400, detail="Category does not exist")

    note.title = updated_note.title
    note.content = updated_note.content
    note.category_id = updated_note.category_id
    db.commit()
    db.refresh(note)
    return note

# Delete a Note
@router.delete("/notes/{note_id}")
def delete_note(note_id: int, db: Session = Depends(get_db)):
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    db.delete(note)
    db.commit()
    return {"message": "Note deleted"}