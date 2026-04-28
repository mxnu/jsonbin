import os
import json
import uuid
import re
from typing import Any, Dict, Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException, Header, Depends, status, Request
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_TOKEN = os.getenv("API_TOKEN", "default-token")
STORAGE_DIR = Path(os.getenv("STORAGE_DIR", "data"))

# Ensure storage directory exists
STORAGE_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="JSONBin Clone")

# Helper to validate ID
def validate_id(bin_id: str):
    if not re.match(r"^[a-zA-Z0-9\-]+$", bin_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid ID format. Only alphanumeric characters and hyphens are allowed."
        )
    return bin_id

# Auth dependency
async def verify_token(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing"
        )
    
    # Check for 'Bearer <token>' format
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization format. Use 'Bearer <TOKEN>'"
        )
    
    token = parts[1]
    if token != API_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

@app.post("/", dependencies=[Depends(verify_token)])
async def create_bin(request: Request):
    try:
        data = await request.json()
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON body")
    
    bin_id = str(uuid.uuid4())
    file_path = STORAGE_DIR / f"{bin_id}.json"
    
    with open(file_path, "w") as f:
        json.dump(data, f)
    
    return {"id": bin_id, "message": "Bin created successfully"}

@app.post("/{bin_id}", dependencies=[Depends(verify_token)])
async def create_bin_with_id(bin_id: str, request: Request):
    validate_id(bin_id)
    file_path = STORAGE_DIR / f"{bin_id}.json"
    
    if file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Bin with this ID already exists. Use PUT to update."
        )
    
    try:
        data = await request.json()
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON body")
    
    with open(file_path, "w") as f:
        json.dump(data, f)
    
    return {"id": bin_id, "message": "Bin created successfully"}

@app.get("/{bin_id}", dependencies=[Depends(verify_token)])
async def get_bin(bin_id: str):
    validate_id(bin_id)
    file_path = STORAGE_DIR / f"{bin_id}.json"
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Bin not found")
    
    with open(file_path, "r") as f:
        data = json.load(f)
    
    return JSONResponse(content=data)

@app.put("/{bin_id}", dependencies=[Depends(verify_token)])
async def update_bin(bin_id: str, request: Request):
    validate_id(bin_id)
    file_path = STORAGE_DIR / f"{bin_id}.json"
    
    try:
        data = await request.json()
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON body")
    
    with open(file_path, "w") as f:
        json.dump(data, f)
    
    return {"id": bin_id, "message": "Bin updated successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
