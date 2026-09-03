import io
import re
import streamlit as st
from openai import OpenAI

# Seitenzentriertes Layout & Titel
st.set_page_config(page_title="OpenAI Text-to-Speech Generator", page_icon="🎙️", layout="centered")

st.title("🎙️ OpenAI Text-to-Speech Generator")
st.markdown("Generiere hochwertige Sprachaufnahmen aus deinen Texten zur Laufzeit.")

# --- SIDEBAR: KONFIGURATION ---
st.sidebar.header("⚙️ Einstellungen")

# 1. API Key Eingabe
api_key_input = st.sidebar.text_input(
    "OpenAI API Key", 
    type="password", 
    placeholder="sk-proj-...",
    help="Dein Schlüssel wird nur lokal für diese Sitzung verwendet und nicht gespeichert."
)

# 2. Modell-Auswahl
model_option = st.sidebar.selectbox(
    "Modell wählen",
    options=["tts-1", "tts-1-hd"],
    index=0,
    help="'tts-1' ist schneller, 'tts-1-hd' bietet eine höhere Audioqualität."
)

# 3. Stimmen-Auswahl
voice_option = st.sidebar.selectbox(
    "Stimme wählen",
    options=["alloy", "echo", "fable", "onyx", "nova", "shimmer"],
    index=4,  # Standardmäßig 'nova'
    help="Wähle den Klangcharakter der Stimme."
)

# 4. Dateiname & Format
file_name_input = st.sidebar.text_input(
    "Dateiname (ohne Endung)", 
    value="mein_audiobook",
    help="Name der Ausgabedatei."
)

format_option = st.sidebar.selectbox(
    "Audio-Format",
    options=["mp3", "opus", "aac", "flac", "wav"],
    index=0
)

# --- HAUPTBEREICH: TEXTEINGABE ---
st.subheader("📝 Texteingabe")
text_input = st.text_area(
    "Füge hier deinen Text ein:", 
    height=250,
    placeholder="Hallo! Das ist ein Test für die Sprachgenerierung..."
)

# Hilfsfunktion zum Aufteilen von Text in Sätze
def split_text_into_sentences(text):
    # Trennt Text bei Satzzeichen (., !, ?) auf, behält den Satzkontext bei
    sentences = re.split(r'(?<=[.!?]) +', text.strip())
    return [s.strip() for s in sentences if s.strip()]

# --- GENERIERUNGS-LOGIK ---
if st.button("🚀 Audio Generieren", type="primary"):
    # Validierung der Eingaben
    if not api_key_input:
        st.error("❌ Bitte gib deinen OpenAI API-Key in der Seitenleiste ein.")
    elif not text_input.strip():
        st.warning("⚠️ Bitte gib zuerst einen Text ein.")
    else:
        try:
            # OpenAI Client mit dem eingegebenen Key initialisieren
            client = OpenAI(api_key=api_key_input)
            
            # Text in Segmente unterteilen für Fortschrittsanzeige
            sentences = split_text_into_sentences(text_input)
            total_sentences = len(sentences)
            
            st.info(f"Insgesamt {total_sentences} Satz-Segmente zu verarbeiten.")
            
            # Progress Bar & Status Text aufsetzen
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            audio_chunks = []
            
            # Schleife durch alle Sätze mit Fortschrittsbalken
            for index, sentence in enumerate(sentences):
                # Status aktualisieren
                status_text.text(f"Verarbeite Segment {index + 1} von {total_sentences}...")
                
                # API-Anfrage stellen
                response = client.audio.speech.create(
                    model=model_option,
                    voice=voice_option,
                    input=sentence,
                    response_format=format_option
                )
                
                # Audiodaten sammeln (Bytes)
                audio_chunks.append(response.content)
                
                # Fortschrittsbalken aktualisieren
                progress = (index + 1) / total_sentences
                progress_bar.progress(progress)
            
            status_text.success("✅ Generierung erfolgreich abgeschlossen!")
            
            # Audio-Chunks zusammenfügen (Byte-Verkettung für Standard MP3)
            complete_audio = b"".join(audio_chunks)
            
            # --- ERGEBNIS-ANZEIGE & DOWNLOAD ---
            st.markdown("---")
            st.subheader("🎧 Ergebnis")
            
            # 1. In-App Audio Player
            st.audio(complete_audio, format=f"audio/{format_option}")
            
            # 2. Download Button
            full_filename = f"{file_name_input.strip() if file_name_input else 'audio'}.{format_option}"
            
            st.download_button(
                label="📥 Audio-Datei herunterladen",
                data=complete_audio,
                file_name=full_filename,
                mime=f"audio/{format_option}",
                type="primary"
            )
            
        except Exception as e:
            st.error(f"❌ Fehler bei der API-Anfrage: {str(e)}")
