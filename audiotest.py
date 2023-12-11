
import elevenlabs
from elevenlabs import VoiceSettings  
from elevenlabs import set_api_key
from elevenlabs import play  
from elevenlabs import generate  
import os

set_api_key("99128584b98eb68e0e4f3289f7386063")


def transcribe_audio(response):
    audio = generate(response, voice = "Bill")
    with open('audio_files/bobs_voice.mp3', 'wb') as file:
        file.write(audio)    

def main():
    transcribe_audio("did it over right")

if __name__ == "__main__":
    main()
