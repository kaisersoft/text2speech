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

# 4. Geschwindigkeits-Regler (Speed)
speed_option = st.sidebar.slider(
    "Sprechgeschwindigkeit (Speed)",
    min_value=0.25,
    max_value=4.0,
    value=1.0,
    step=0.05,
    help="1.0 ist Standard. Höhere Werte sprechen schneller, niedrigere langsamer."
)

# 5. Dateiname & Format
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

# --- HAUPTBEREICH: TEXTEINGABE & STATISTIKEN ---
st.subheader("📝 Texteingabe")

text_input = st.text_area(
    "Füge hier deinen Text ein:", 
    height=250,
    placeholder="Hallo! Das ist ein Test für die Sprachgenerierung..."
)

# Metriken berechnen
char_count = len(text_input)
word_count = len(text_input.split()) if text_input.strip() else 0

# Schätzung der Audiodauer: Durchschnittlich ~150 Wörter pro Minute bei 1.0x Speed
base_wpm = 150
adjusted_wpm = base_wpm * speed_option
estimated_minutes = word_count / adjusted_wpm if adjusted_wpm > 0 else 0

# Anzeige von Zähler und Schätzung
col1, col2, col3 = st.columns(3)
col1.metric("Anzahl Zeichen", f"{char_count} / 4.096")
col2.metric("Anzahl Wörter", f"{word_count}")
col3.metric("Geschätzte Länge", f"~{estimated_minutes:.1f} Min")

# Zeichen-Cap Warnung / Hinweis
if char_count > 4096:
    st.warning(
        f"⚠️ **Hinweis:** Dein Text überschreitet das OpenAI-Limit von 4.096 Zeichen pro Einzelanfrage "
        f"({char_count} Zeichen). Die App teilt den Text automatisch in Abschnitte auf, um ihn komplett zu verarbeiten."
    )

# Hilfsfunktion zum Aufteilen von Text in Sätze
def split_text_into_sentences(text):
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
                
                # API-Anfrage stellen (inkl. speed-Parameter)
                response = client.audio.speech.create(
                    model=model_option,
                    voice=voice_option,
                    input=sentence,
                    speed=speed_option,
                    response_format=format_option
                )
                
                # Audiodaten sammeln (Bytes)
                audio_chunks.append(response.content)
                
                # Fortschrittsbalken aktualisieren
                progress = (index + 1) / total_sentences
                progress_bar.progress(progress)
            
            status_text.success("✅ Generierung erfolgreich abgeschlossen!")
            
            # Audio-Chunks zusammenfügen
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
