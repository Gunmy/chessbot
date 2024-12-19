#Run with "fastapi dev api_point.py"

from typing import Union

from fastapi import FastAPI

app = FastAPI()

@app.get("/eval")
async def evaluate(position: str):
    return {"position": position}


