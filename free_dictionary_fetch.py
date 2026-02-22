import requests
import sys

def get_pronunciation(word: str) -> str:
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    print(f"Fetching: {url}")
    
    try:
        # Adding a User-Agent header is good practice
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
        
        data = response.json()
        
        # The API returns a list of entries for the word
        if isinstance(data, list) and len(data) > 0:
            phonetics = data[0].get("phonetics", [])
            
            # Iterate through phonetics to find the first one with a valid audio link
            for phonetic in phonetics:
                audio_url = phonetic.get("audio")
                if audio_url:
                    return audio_url
                    
        return "No audio pronunciation found."
        
    except requests.exceptions.HTTPError as e:
        if response.status_code == 404:
            return f"Word '{word}' not found in the dictionary."
        return f"HTTP Error: {response.status_code} - {e}"
    except requests.exceptions.RequestException as e:
        return f"Error fetching data: {e}"

if __name__ == "__main__":
    # Default to 'diarize' if no argument is provided
    word = "diarize"
    if len(sys.argv) > 1:
        word = sys.argv[1]
        
    audio_url = get_pronunciation(word)
    print(f"\nWord: {word}")
    print(f"Pronunciation Audio URL: {audio_url}")
