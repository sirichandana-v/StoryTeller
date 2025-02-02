import time
import asyncio
import edge_tts
import sounddevice as sd
import numpy as np
from io import BytesIO
from pydub import AudioSegment
from groq import Groq
import os
from dotenv import load_dotenv
import tempfile
import soundfile as sf

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

def text_to_speech(text):
    """Converts text to speech using Edge TTS and plays it."""
    mp3_stream = BytesIO()
    communicate = edge_tts.Communicate(text, "en-US-AriaNeural")
    
    async def stream_audio():
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                mp3_stream.write(chunk["data"])
        
        mp3_stream.seek(0)
        audio = AudioSegment.from_file(mp3_stream, format="mp3")
        wav_stream = BytesIO()
        audio.export(wav_stream, format="wav")
        wav_stream.seek(0)
        
        samples = np.array(audio.get_array_of_samples(), dtype=np.float32)
        samples /= np.iinfo(audio.array_type).max  # Normalize
        
        sd.play(samples, samplerate=audio.frame_rate)
        sd.wait()
    
    asyncio.run(stream_audio())

def transcribe_audio():
    """Records audio from the microphone and transcribes it using Groq ASR."""
    print("🎤 Listening... Speak now!")
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_wav:
        duration = 10  # Adjust duration if needed
        sample_rate = 16000
        audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='int16')
        sd.wait()
        sf.write(temp_wav.name, audio_data, sample_rate)
        temp_wav_path = temp_wav.name
    
    with open(temp_wav_path, "rb") as audio_file:
        response = client.audio.transcriptions.create(
            model="whisper-large-v3",
            file=audio_file,
            language="en"
        )
    os.remove(temp_wav_path)
    return response.text

def generate_story(prompt):
    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    return response.choices[0].message.content

def main():
    print("👴 Grandpa: Well hello there, young one! What kind of story do you want to hear today?")
    text_to_speech("Well hello there, young one! What kind of story do you want to hear today?")
    story_type = transcribe_audio()
    print("You:", story_type)

    prompt = f"""Tell me a {story_type} story in the voice of an old, wise grandpa. 
    Speak as if you are telling the story to a child, with warmth, humor, and dramatic pauses. 
    Pause when you want the listener to give an idea about what happens next. 
    When you want input, clearly ask something like: 'What do you think should happen next?' or 'Should the hero go left or right?'
    Always continue from the user's suggestion while keeping the grandpa storytelling style alive."""
    
    story = generate_story(prompt)
    
    while True:
        sentences = story.split('. ')
        for sentence in sentences:
            print("👴 Grandpa:", sentence)
            text_to_speech(sentence)
            time.sleep(1)
            
            if "what do you think" in sentence.lower() or "should" in sentence.lower() or "what happens next" in sentence.lower():
                print("👴 Grandpa: I'm listening... what should happen next?")
                text_to_speech("I'm listening... what should happen next?")
                user_input = transcribe_audio()
                print("You:", user_input)
                
                if user_input.lower() in ["stop", "exit", "end"]:
                    print("👴 Grandpa: Alright then, we'll continue another time! *chuckles*")
                    text_to_speech("Alright then, we'll continue another time! *chuckles*")
                    return
                
                story = generate_story(f"""Grandpa chuckles and nods after hearing: "{user_input}". 
He strokes his beard, responding with warmth, humor, or a bit of old wisdom. 
Then, he naturally weaves the suggestion into the story and continues telling it as an old wise storyteller. 
Make sure Grandpa stays fully in character and does NOT explain what he is doing.
""")
                break

if __name__ == "__main__":
    main()
