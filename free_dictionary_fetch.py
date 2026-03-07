import requests
import sys
from urllib.parse import quote

def get_pronunciation(word: str) -> str:
    if not word:
        return "No word provided."
    encoded_word = quote(word)
    return f"https://translate.google.com/translate_tts?ie=UTF-8&q={encoded_word}&tl=en&client=tw-ob"

if __name__ == "__main__":
    # Default to 'diarize' if no argument is provided
    word = "diarize"
    if len(sys.argv) > 1:
        word = sys.argv[1]
        
    audio_url = get_pronunciation(word)
    print(f"\nWord: {word}")
    print(f"Pronunciation Audio URL: {audio_url}")
