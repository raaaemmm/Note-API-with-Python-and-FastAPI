from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from database import engine, Base
from routes import router
import logging
import time
import uuid

# Configure more advanced logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        # Uncomment to add file logging
        # logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app with additional metadata
app = FastAPI(
    title="Notes Management API",
    description="A robust API for managing notes and categories",
    version="1.0.0",
    contact={
        "name": "API Support",
        "email": "riththeara.thr@gmail.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    }
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Logging middleware for request tracking
@app.middleware("http")
async def logging_middleware(request, call_next):
    request_id = str(uuid.uuid4())
    logger.info(f"Request ID: {request_id} | Method: {request.method} | Path: {request.url.path}")
    start_time = time.time()
    
    try:
        response = await call_next(request)
    except Exception as e:
        logger.error(f"Request ID: {request_id} | Error: {str(e)}")
        return JSONResponse(
            status_code=500, 
            content={"request_id": request_id, "message": "Internal Server Error"}
        )
    
    process_time = (time.time() - start_time) * 1000
    logger.info(
        f"Request ID: {request_id} | "
        f"Status Code: {response.status_code} | "
        f"Process Time: {process_time:.2f} ms"
    )
    
    return response

# Create database tables only if not exist
@app.on_event("startup")
def on_startup():
    try:
        logger.info("Starting application initialization...")
        
        # Create database tables
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully.")
        
        # Optional: Add seed data or initial setup
        seed_initial_data()
        
        logger.info("Application startup complete.")
    except Exception as e:
        logger.error(f"Critical error during startup: {e}")
        raise HTTPException(status_code=500, detail="Application initialization failed")

# Optional function to seed initial data
def seed_initial_data():
    """
    Optional method to add initial categories or default data
    when the application starts for the first time.
    """
    from database import SessionLocal
    from models import Category
    
    db = SessionLocal()
    
    try:
        # Check if any categories exist
        existing_categories = db.query(Category).count()
        
        if existing_categories == 0:
            # add some default categories
            default_categories = [
                Category(name="Personal"),
                Category(name="Work"),
                Category(name="Ideas"),
                Category(name="Reminder")
            ]
            
            db.add_all(default_categories)
            db.commit()
            logger.info("Added default categories to the database.")
    except Exception as e:
        logger.warning(f"Error seeding initial data: {e}")
        db.rollback()
    finally:
        db.close()

# Register routes (Prefix all routes with `/api`)
app.include_router(router, prefix="/api")

# Root Endpoint with more detailed information
@app.get("/")
def root():
    return {
        "message": "Welcome to the Notes Management API!",
        "version": "1.0.0",
        "documentation": "/docs",
        "signature": "Build with ❤ by: Raaaemmm (◉_◉)"
    }

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "API is up and running"}