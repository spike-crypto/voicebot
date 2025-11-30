#!/usr/bin/env python3
"""
Simple provider connectivity checks for this project.

This script checks:
- Hugging Face Inference API (model metadata endpoint)
- OpenAI API (models list)
- Groq presence (basic import + API key check)
- Whisper import and ffmpeg availability

Usage: run from repository root or backend directory so dotenv loads correctly.

PowerShell example:
    cd backend
    .\.venv\Scripts\Activate.ps1
    python test_providers.py

Note: This script performs live network calls and requires the appropriate
API keys present in `backend/.env` or the environment:
- HUGGINGFACE_API_TOKEN
- OPENAI_API_KEY
- GROQ_API_KEY (optional)

The script is intentionally lightweight and prints results for each provider.
"""

import os
import sys
import json
import shutil
import requests
from dotenv import load_dotenv
from pathlib import Path

# Load backend .env automatically relative to this file
HERE = Path(__file__).resolve().parent
load_dotenv(HERE / '.env')


def ok(msg):
    print(f"[OK] {msg}")


def fail(msg):
    print(f"[FAIL] {msg}")


def check_huggingface(model=None):
    token = os.environ.get('HUGGINGFACE_API_TOKEN')
    model = model or os.environ.get('HUGGINGFACE_STT_MODEL', 'openai/whisper-small')
    if not token:
        fail('Hugging Face: HUGGINGFACE_API_TOKEN not set')
        return False
    # Try a lightweight reachability check (GET) first
    url = f'https://api-inference.huggingface.co/models/{model}'
    headers = {'Authorization': f'Bearer {token}'}
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        if resp.status_code == 200:
            ok(f'Hugging Face model metadata reachable: {model}')
        else:
            # Not necessarily fatal — some speech models require POST with audio
            fail(f'Hugging Face metadata responded {resp.status_code}: {resp.text[:200]}')

        # Now try a POST with a small generated WAV sample to test audio upload
        try:
            from io import BytesIO
            import wave
            import math

            # Generate a 1 second 16kHz mono sine wave for testing
            samplerate = 16000
            duration_s = 1.0
            frequency = 440.0
            n_frames = int(samplerate * duration_s)
            buf = BytesIO()
            with wave.open(buf, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(samplerate)
                import struct
                for i in range(n_frames):
                    t = i / samplerate
                    value = int(32767.0 * 0.2 * math.sin(2.0 * math.pi * frequency * t))
                    wf.writeframes(struct.pack('<h', value))
            buf.seek(0)

            post_headers = {'Authorization': f'Bearer {token}'}
            files = {'file': ('test.wav', buf, 'audio/wav')}
            post_resp = requests.post(url, headers=post_headers, files=files, timeout=60)
            if post_resp.status_code == 200:
                ok(f'Hugging Face accepted audio POST for model {model}')
                return True
            else:
                fail(f'Hugging Face audio POST failed {post_resp.status_code}: {post_resp.text[:300]}')
                return False
        except Exception as e:
            fail(f'Hugging Face audio POST error: {e}')
            return False

    except Exception as e:
        fail(f'Hugging Face request error: {e}')
        return False


def check_openai():
    key = os.environ.get('OPENAI_API_KEY')
    if not key:
        fail('OpenAI: OPENAI_API_KEY not set')
        return False
    try:
        import openai
        openai.api_key = key
        try:
            models = openai.Model.list()
            ok(f'OpenAI reachable, returned {len(models.data)} models')
            return True
        except Exception as e:
            fail(f'OpenAI API call failed: {e}')
            return False
    except Exception as e:
        fail(f'OpenAI SDK not available or error importing: {e}')
        return False


def check_groq():
    key = os.environ.get('GROQ_API_KEY')
    try:
        import groq
        # If API key missing we still consider import ok but warn
        if not key:
            fail('Groq API key not set (GROQ_API_KEY) — import ok')
            return False
        ok('Groq package import ok; GROQ_API_KEY set')
        return True
    except Exception as e:
        fail(f'Groq import or config issue: {e}')
        return False


def check_whisper_ffmpeg():
    try:
        import whisper
        ffmpeg = shutil.which('ffmpeg')
        if not ffmpeg:
            fail('ffmpeg not found in PATH')
            return False
        ok(f'Whisper import ok and ffmpeg found at {ffmpeg}')
        return True
    except Exception as e:
        fail(f'Whisper import or ffmpeg check failed: {e}')
        return False


def main():
    print('Provider checks starting...')
    results = {}

    results['huggingface'] = check_huggingface()
    results['openai'] = check_openai()
    results['groq'] = check_groq()
    results['whisper_ffmpeg'] = check_whisper_ffmpeg()

    print('\nSummary:')
    for k, v in results.items():
        print(f' - {k}: {"OK" if v else "FAIL"}')

    overall = all(results.values())
    if overall:
        ok('All provider checks passed')
        sys.exit(0)
    else:
        fail('Some provider checks failed — see messages above')
        sys.exit(2)


if __name__ == '__main__':
    main()
