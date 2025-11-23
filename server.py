from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List,Dict
from datetime import datetime
import uvicorn
from main import SQLMetadataExtractor 
# Pydantic models for request/response validation
def clean_sql(query: str) -> str:
    # Remove line breaks and excess whitespace
    cleaned = " ".join(query.split())
    # Ensure ending semicolon only once
    cleaned = cleaned.rstrip(";") + ";"
    return cleaned
def createString(type,link,password,username,database):
    type=type.strip()
    type=type.lower()
    if  type=="mysql":
        return f"mysql+pymysql://{username}:{password}@{link}/{database}"
    
    return "mysql+pymysql://root:root@localhost:3308/llm"
class ItemQuery(BaseModel):
    userId:str= Field(..., min_length=1, max_length=100)
    query:str= Field(..., min_length=1, max_length=100)
class ItemBase(BaseModel):
    link: str = Field(..., min_length=1, max_length=100)
    username: str = Field(..., min_length=1, max_length=100)
    password:str= Field(..., min_length=1, max_length=100)
    database:str = Field(..., min_length=1, max_length=100)
    userId:str= Field(..., min_length=1, max_length=100)
    type:str= Field(..., min_length=1, max_length=100)
   
class Response(BaseModel):
    created_at:datetime
    res:str = Field(..., min_length=1, max_length=100)




# Initialize FastAPI app
app = FastAPI(
    title="Generic FastAPI Application",
    description="A generic REST API built with FastAPI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory database (replace with real database in production)
items_db:Dict[str,SQLMetadataExtractor]  = {}
item_id_counter = ""

# Dependency for getting items


# Routes
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint returning API information"""
    return {
        "message": "Welcome to the Generic FastAPI Application",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow()
    }

@app.post("/items", response_model=Response, status_code=status.HTTP_201_CREATED)
async def create_item(item: ItemBase):
    """Create a new item"""
    global item_id_counter
    connection=createString(item.type,item.link,item.password,item.username,item.database)
    items_db[item.userId]=SQLMetadataExtractor(connection,item.userId)
  #  now = datetime.utcnow()
    now=datetime.utcnow()
   
    return  Response(created_at=now,res="hello")

@app.post("/query", response_model=Response)
async def list_items(
    item:ItemQuery
):
    """List all items with optional filtering"""
    model=items_db[item.userId]
    val=clean_sql(model.generate_response(item.query))
    res=Response(created_at=datetime.utcnow(),res=val)
   
  
    
    return res

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )