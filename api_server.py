#!/usr/bin/env python3

from flask import Flask, request, jsonify
import whisper
import ffmpeg
import numpy as np
from io import BytesIO
import base64

app = Flask(__name__)

ssl_context = ("server.crt", "server.key")

def load_audio(file_bytes: bytes, sr: int = 16_000) -> np.ndarray:
    """
    Use file's bytes and transform to mono waveform, resampling as necessary
    Parameters
    ----------
    file: bytes
        The bytes of the audio file
    sr: int
        The sample rate to resample the audio if necessary
    Returns
    -------
    A NumPy array containing the audio waveform, in float32 dtype.
    """
    try:
        # This launches a subprocess to decode audio while down-mixing and resampling as necessary.
        # Requires the ffmpeg CLI and `ffmpeg-python` package to be installed.
        out, _ = (
            ffmpeg.input('pipe:', threads=0)
            .output("pipe:", format="s16le", acodec="pcm_s16le", ac=1, ar=sr)
            .run_async(pipe_stdin=True, pipe_stdout=True)
        ).communicate(input=file_bytes)

    except ffmpeg.Error as e:
        raise RuntimeError(f"Failed to load audio: {e.stderr.decode()}") from e

    return np.frombuffer(out, np.int16).flatten().astype(np.float32) / 32768.0

# Load the base model from the Whisper AI platform
print("Loading model...")
model = whisper.load_model("medium")
print("Loaded.")

@app.route("/transcribe", methods=["POST"])
def transcribe():
    # Get the base64 encoded MP3 file from the request body
    mp3_file = request.json["audio_file"]

    # Decode the base64 string to get the binary data
    mp3_data = base64.b64decode(mp3_file)

    audio = load_audio(mp3_data)

    # Transcribe the MP3 file using Whisper
    print("Transcribing...")
    transcript = model.transcribe(audio, task="translate")

    print("Complete!")

    # Return the JSON output from Whisper
    return jsonify({"transcription": transcript})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000, ssl_context=ssl_context)
