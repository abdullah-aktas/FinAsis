from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

app = FastAPI(title="FinAsis Marketplace")

class Content(BaseModel):
    id: Optional[str]
    title: str
    description: str
    author: str
    type: str  # game, task, scenario
    rating: float
    downloads: int
    price: float

class ContentDB:
    def __init__(self):
        self.contents = {}

    async def add_content(self, content: Content):
        content.id = str(len(self.contents) + 1)
        self.contents[content.id] = content
        return content

db = ContentDB()

@app.post("/content/", response_model=Content)
async def create_content(content: Content):
    return await db.add_content(content)

@app.get("/content/{content_id}", response_model=Content)
async def read_content(content_id: str):
    if content_id not in db.contents:
        raise HTTPException(status_code=404, detail="Content not found")
    return db.contents[content_id]

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
