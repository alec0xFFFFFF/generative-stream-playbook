import requests

url = "http://localhost:8000/"

with requests.get(url, stream=True) as r:
    for chunk in r.iter_content(1024):  # or, for line in r.iter_lines():
        print(chunk)

import requests
from pydub import AudioSegment
from pydub.playback import play
import io


def stream_audio(url):
    # Connect to the streaming endpoint
    with requests.get(url, stream=True) as response:
        # Check if the request was successful
        response.raise_for_status()

        # Convert streamed bytes into audio
        audio_data = io.BytesIO(response.content)
        audio = AudioSegment.from_file(audio_data, format="mp3")

        # Play the audio
        play(audio)


if __name__ == "__main__":
    stream_url = "http://localhost:8000/stream_audio"  # Replace with your FastAPI endpoint
    stream_audio(stream_url)