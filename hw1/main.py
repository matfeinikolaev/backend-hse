import uvicorn
import time
import asyncio
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Payload(BaseModel):
    numbers: list
    delays: list

class Result(BaseModel):
    number: float
    square: float
    delay: float
    time: float

class Response(BaseModel):
    results: list
    total_time: float
    parallel_faster_than_sequential: bool

async def async_task(num: float, delay: float) -> Result:
    start = time.time()
    await asyncio.sleep(delay)
    square = num**2
    duration = time.time() - start
    return {"number": num, "square": square, "delay": delay, "time": duration}

@app.post("/calculate")
async def calculate(pl: Payload) -> Response:
    start = time.time()
    total_delay = sum([delay for delay in pl.delays])
    tasks = []
    for i, num in enumerate(pl.numbers):
        delay = pl.delays[i]
        tasks.append(asyncio.create_task(async_task(num, delay)))

    results = await asyncio.gather(*tasks)
    total_time = time.time() - start

    return {
        "results": results,
        "total_time": total_time,
        "parallel_faster_than_sequential": total_time < total_delay
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )