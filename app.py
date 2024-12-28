import streamlit as st
import streamlit.components.v1 as components
import sounddevice as sd
import numpy as np
import pyttsx3
import pywhatkit
import datetime
import wikipedia
import pyjokes
import speech_recognition as sr
import threading
import sounddevice as sd

# Initialize recognizer and text-to-speech engine
listener = sr.Recognizer()
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

# Initialize session state for video
if "current_video" not in st.session_state:
    st.session_state["current_video"] = None

# Function to convert text to speech (thread-safe)
def talk(text):
    """Converts text to speech in a separate thread to avoid conflicts."""
    def speak():
        engine.say(text)
        engine.runAndWait()

    thread = threading.Thread(target=speak)
    thread.start()

# Function to capture voice command
def take_command():
    """Listens to the user's voice command using sounddevice."""
    try:
        st.info("Listening... Please speak now!")
        # Record audio
        duration = 5  # seconds
        sample_rate = 16000
        recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype="int16")
        sd.wait()  # Wait for the recording to finish

        # Convert recorded audio to text
        audio_data = np.frombuffer(recording, dtype=np.int16).tobytes()
        command = listener.recognize_google(sr.AudioData(audio_data, sample_rate, 2))
        command = command.lower()
        st.write(f"Command received: {command}")
        return command
    except sr.UnknownValueError:
        st.error("I couldn't understand what you said. Please try again.")
    except Exception as e:
        st.error(f"Error: {e}")
    return None

# Function to embed and autoplay YouTube videos with controls
def display_video(video_url):
    """Embeds a YouTube video with autoplay enabled and controls for unmuting."""
    # Extract video ID from the URL
    if "youtube.com/watch?v=" in video_url:
        video_id = video_url.split("v=")[-1]
    elif "youtu.be/" in video_url:
        video_id = video_url.split("/")[-1]
    else:
        st.error("Invalid YouTube URL")
        return

    # Create an iframe HTML string with autoplay and controls
    iframe_html = f"""
    <iframe width="560" height="315" src="https://www.youtube.com/embed/{video_id}?autoplay=1&controls=1" 
    frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>
    """
    # Embed the iframe in Streamlit
    components.html(iframe_html, height=315)

# Function to process the command
def run_alexa(command):
    """Processes the command and performs actions."""
    if "play" in command:
        song = command.replace("play", "").strip()
        talk(f"Playing {song}")

        # Get YouTube video link
        try:
            video_url = pywhatkit.playonyt(song, open_video=False)
            st.session_state["current_video"] = video_url  # Save video URL to session state
            st.success(f"Playing {song} on YouTube.")
        except Exception as e:
            st.error(f"Error finding the song on YouTube: {e}")
    elif "stop" in command:
        if st.session_state["current_video"]:
            st.session_state["current_video"] = None  # Clear the current video
            talk("Stopping the song.")
            st.success("Song stopped.")
        else:
            talk("No song is currently playing.")
            st.warning("No song is currently playing.")
    elif "time" in command:
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        talk(f"The current time is {current_time}")
        st.success(f"The current time is {current_time}.")
    elif "who is" in command:
        person = command.replace("who is", "").strip()
        info = wikipedia.summary(person, sentences=1)
        talk(info)
        st.success(f"Here's what I found: {info}")
    elif "date" in command:
        talk("Sorry, I have a headache.")
        st.warning("Sorry, I have a headache.")
    elif "are you single" in command:
        talk("I'm in a relationship with WiFi.")
        st.success("I'm in a relationship with WiFi.")
    elif "joke" in command:
        joke = pyjokes.get_joke()
        talk(joke)
        st.success(f"Here's a joke for you: {joke}")
    else:
        talk("Please say the command again.")
        st.error("I didn't understand your command. Please try again.")

# Streamlit UI
st.title("Voice Assistant")
st.write("Time Inquiry: Say, What time is it")
st.write("Wikipedia Search: Say, Who is person_Name")
st.write("Jokes: Say, Tell me a joke")
st.write("Play Songs: Say, Play song_name")
st.write("Stop Songs: Say, Alexa, please stop the song")

st.write("Use this voice assistant by clicking the button below and speaking into your microphone.")
if st.button("Activate Voice Assistant"):
    command = take_command()
    if command:
        run_alexa(command)
    else:
        st.error("No valid command received. Please try again.")

# Display the currently playing video if any
if st.session_state["current_video"]:
    display_video(st.session_state["current_video"])
print("Sounddevice is working correctly!")