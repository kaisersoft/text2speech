import os
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

# Lädt die Variablen aus der .env-Datei in die Umgebung
load_dotenv()

# Der OpenAI-Client zieht sich den Key nun automatisch
client = OpenAI()
# Client initialisieren (greift automatisch auf die Umgebungsvariable OPENAI_API_KEY zu)
client = OpenAI()

# Pfad festlegen, wo die MP3-Datei gespeichert werden soll
speech_file_path = Path(__file__).parent / "speech.mp3"

# API-Aufruf durchführen
response = client.audio.speech.create(
    model="tts-1",           # Standard-Modell (oder "tts-1-hd" für höhere Qualität)
    voice="onyx",           # Stimme wählen (z.B. alloy, echo, fable, onyx, nova, shimmer)
    input="Hallo! Das ist ein Test der OpenAI Text-to-Speech API auf Deutsch."
)

# Audio-Datei auf der Festplatte speichern
response.stream_to_file(speech_file_path)

print(f"Audio erfolgreich gespeichert unter: {speech_file_path}")
