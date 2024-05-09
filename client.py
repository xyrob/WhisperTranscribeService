#!/usr/bin/env python3

import sys
import json
import base64
import requests

# Read the mp3 file from disk
with open(sys.argv[1], "rb") as f:
    audio_data = f.read()

# Encode the data to base64
encoded_data = base64.b64encode(audio_data)

# Create a JSON object with the encoded data
json_obj = {"audio_file": encoded_data.decode()}

# Submit the JSON object to the API endpoint
response = requests.post("https://127.0.0.1:5000/transcribe", json=json_obj, verify=False)

# Print the response
print(response.text)
