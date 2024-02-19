import requests
import json
import sseclient
import os
from dotenv import load_dotenv
import openai

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


def streamResponse():
    prompt = "explain server sent events"
    completion = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=[{"role": "user", "content": prompt}],
        stream=True)
    for line in completion:
        chunk = line['choices'][0].get('delta', {}).get('content', '')
        print(line)
        if chunk:
            print("chunk")
            yield chunk


## flask code
# @app.route('/completions/chat', methods=['POST'])
# def completion_api():
#     def stream():
#         completion = openai.ChatCompletion.create(
#             model='gpt-3.5-turbo',
#             messages=[{"role": "user", "content": request.get_json().get('prompt')}],
#             stream=True)
#         for line in completion:
#             chunk = line['choices'][0].get('delta', {}).get('content', '')
#             if chunk:
#                 yield chunk
#     return flask.Response(stream(), mimetype='text/event-stream')

def streamElevenLabs():
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream"

    payload = {
        "model_id": model_id,
        "text": "hello world",
        "voice_settings": {
            "similarity_boost": 123,
            "stability": 123,
            "style": 123,
            "use_speaker_boost": True
        }
    }
    headers = {"Content-Type": "application/json"}

    response = requests.request("POST", url, json=payload, headers=headers)

    print(response.text)


def streamResponse():
    reqUrl = 'https://api.openai.com/v1/completions'
    reqHeaders = {
        'Accept': 'text/event-stream',
        'Authorization': 'Bearer ' + API_KEY
    }

    reqBody = {
        "model": 'gpt-3.5-turbo',
        "messages": {
            {"role": "user",
             "content": "prompt"}
        },
        "max_tokens": 100,
        "temperature": 0,
        "stream": True
    }
    request = requests.post(reqUrl, stream=True, headers=reqHeaders, json=json.dumps(reqBody))
    client = sseclient.SSEClient(request)
    for event in client.events():
        if event.data != '[DONE]':
            print(json.loads(event.data)['choices'][0]['text'], end="", flush=True)


if __name__ == '__main__':
    streamResponse()
