import os
from deepgram import DeepgramClient
from dotenv import load_dotenv

load_dotenv()

DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")


def transcribe_audio(audio_data: bytes) -> str:
    """
    Transcribes audio bytes using Deepgram.
    """
    if not DEEPGRAM_API_KEY:
        return "Error: DEEPGRAM_API_KEY not configured."

    try:
        deepgram = DeepgramClient(DEEPGRAM_API_KEY)

        payload = {
            "buffer": audio_data,
        }

        options = {
            "model": "nova-2",
            "smart_format": True,
        }

        response = deepgram.listen.prerecorded.v("1").transcribe_file(payload, options)
        return response.results.channels[0].alternatives[0].transcript

    except Exception as e:
        print(f"Deepgram Error: {e}")
        return "Error transcribing audio."
