from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import asyncio

app = FastAPI()


async def fake_data_streamer():
    for i in range(10):
        yield b'this is fake: {}\n\n'
        await asyncio.sleep(0.5)


@app.get('/')
async def main():
    return StreamingResponse(fake_data_streamer(), media_type='text/event-stream')


@app.get("/stream_audio")
async def stream_audio():
    def iterfile():
        with open("path_to_audio_file.mp3", mode="rb") as file_like:
            yield from file_like

    return StreamingResponse(iterfile(), media_type="audio/mpeg")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
