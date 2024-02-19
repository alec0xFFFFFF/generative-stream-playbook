from flask import Flask, request, Response, stream_with_context
import asyncio
import json
import base64
import os
import websockets
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

# Initialize Flask and Flask-Asyncio
app = Flask(__name__)

ELEVENLABS_API_KEY = os.getenv("ELEVEN_LABS_API_KEY")
VOICE_ID = '21m00Tcm4TlvDq8ikWAM'
# Initialize OpenAI client
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
aclient = AsyncOpenAI(api_key=OPENAI_API_KEY)


# Async route for text-to-speech conversion
@app.route('/tts', methods=['POST'])
async def tts():
    data = request.json
    user_query = data['query']
    audio_stream = asyncio.create_task(chat_completion(user_query))
    return Response(stream_with_context(audio_stream_generator(audio_stream)), mimetype='audio/mpeg')


# Your existing async functions (chat_completion, text_to_speech_input_streaming, etc.)
# ...

async def text_chunker(chunks):
    """Split text into chunks, ensuring to not break sentences."""
    splitters = (".", ",", "?", "!", ";", ":", "—", "-", "(", ")", "[", "]", "}", " ")
    buffer = ""

    async for text in chunks:
        if buffer.endswith(splitters):
            yield buffer + " "
            buffer = text
        elif text.startswith(splitters):
            yield buffer + text[0] + " "
            buffer = text[1:]
        else:
            buffer += text

    if buffer:
        yield buffer + " "


async def chat_completion(query):
    """Retrieve text from OpenAI and pass it to the text-to-speech function."""
    response = await aclient.chat.completions.create(model='gpt-4', messages=[{'role': 'user', 'content': query}],
                                                     temperature=1, stream=True)

    async def text_iterator():
        async for chunk in response:
            delta = chunk.choices[0].delta
            print(delta.content)
            yield delta.content

    await text_to_speech_input_streaming(VOICE_ID, text_iterator())


async def text_to_speech_input_streaming(voice_id, text_iterator):
    """Send text to ElevenLabs API and stream the returned audio."""
    uri = f"wss://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream-input?model_id=eleven_monolingual_v1"

    async with websockets.connect(uri) as websocket:
        await websocket.send(json.dumps({
            "text": " ",
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.8},
            "xi_api_key": ELEVENLABS_API_KEY,
        }))

        async def listen():
            """Listen to the websocket for audio data and yield it."""
            while True:
                try:
                    message = await websocket.recv()
                    data = json.loads(message)
                    if data.get("audio"):
                        yield base64.b64decode(data["audio"])
                    elif data.get('isFinal'):
                        break
                except websockets.exceptions.ConnectionClosed:
                    print("Connection closed")
                    break

        listen_generator = listen()

        async for text in text_chunker(text_iterator):
            await websocket.send(json.dumps({"text": text, "try_trigger_generation": True}))

        await websocket.send(json.dumps({"text": ""}))

        # Instead of creating a separate task, return the generator itself
        return listen_generator


# Generator function to adapt the audio stream for Flask Response
async def audio_stream_generator(audio_stream):
    async for chunk in audio_stream:
        yield chunk


# Main execution
if __name__ == "__main__":
    app.run(debug=True)
