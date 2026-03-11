import json

import requests


OPENCODE_HOST = '127.0.0.1'
OPENCODE_PORT = 0
OPENCODE_PASSWORD = None


def request(method, path, **kwargs):
    url = f'http://{OPENCODE_HOST}:{OPENCODE_PORT}/{path.lstrip("/")}'
    if OPENCODE_PASSWORD:
        kwargs['auth'] = ('opencode', OPENCODE_PASSWORD)
    return requests.request(method, url, **kwargs)


def global_health():
    return request('get', '/global/health').json()


def start_session():
    session = request("post",'/session', json={}).json()
    return session['id']


def text_prompt_async(session_id, prompt, provider_id='openai', model_id='gpt-5.3-codex'):
    assert request("post", f'/session/{session_id}/prompt_async', json={
        "model": {
            "providerID": provider_id,
            "modelID": model_id,
        },
        "parts": [
            {
                "type": "text",
                "text": prompt,
            }
        ]
    }).status_code == 204


def iterate_events():
    with request('get', '/event', stream=True) as response:
        for line in response.iter_lines():
            if line.startswith(b'data: {'):
                yield json.loads(line[6:])


def text_prompt_sync(session_id, *args, **kwargs):
    for i, event in enumerate(iterate_events()):
        if i == 0:
            assert event['type'] == 'server.connected'
            text_prompt_async(session_id, *args, **kwargs)
        elif event['type'] == 'session.idle' and event['properties'].get('sessionID') == session_id:
            break
    last_message = request("get", f'/session/{session_id}/message').json()[-1]
    texts = []
    for part in last_message['parts']:
        if part['type'] == 'text':
            texts.append(part['text'])
    return '\n'.join(texts)
