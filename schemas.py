from pydantic import BaseModel

# Category Schemas
class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: int

    class Config:
        from_attributes = True  # Correct for Pydantic V2

# Note Schemas
class NoteBase(BaseModel):
    title: str
    content: str

class NoteCreate(NoteBase):
    category_id: int  # Changed from category string to category_id integer

class NoteResponse(BaseModel):
    id: int
    title: str
    content: str
    category: CategoryResponse  # Include full category details

    class Config:
        from_attributes = True