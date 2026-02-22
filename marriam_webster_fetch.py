import requests
from bs4 import BeautifulSoup
import sys

def get_short_definition(word: str) -> tuple[str, str]:
    # Construct the URL
    url = f'https://www.merriam-webster.com/dictionary/{word}'
    print(f"Fetching: {url}")
    
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching page: {e}")
        return "", ""

    soup = BeautifulSoup(response.content, 'html.parser')

    # Method 1: Get all definition texts from the main dictionary entry
    # Merriam-Webster usually wraps definitions in <span class="dtText">
    definitions: list[str] = []
    
    # Check for the primary specific definitions first
    dt_elements = soup.find_all('span', class_='dtText')
    
    for dt in dt_elements:
        # Get text, strip whitespace, and remove the leading colon if present
        text = dt.get_text().strip()
        if text.startswith(':'):
            text = text[1:].strip()
        if text:
            definitions.append(text)

    # Method 2: Fallback to meta description if no specific definitions found
    # (Sometimes useful for a quick summary)
    if not definitions:
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            content = meta_desc.get('content', '')
            # The meta description often follows "Word definition is - ..." format
            if ' definition is - ' in content:
                short_part = content.split(' definition is - ')[1].split('. How to use')[0]
                definitions.append(short_part)
            else:
                definitions.append(content)

    # Method 3: Get pronunciation audio URL
    sound_url = ""
    play_button = soup.find('a', class_='play-pron-v2')
    if play_button and play_button.has_attr('data-file'):
        sound_file_name = play_button['data-file']
        # The directory is usually the first letter of the file name, or 'gg' if it starts with 'gg', etc.
        # But Merriam-Webster API uses the first letter or specific rules.
        # The data-dir attribute sometimes exists, but if not, we can fallback to the first letter.
        sound_dir = play_button.get('data-dir', sound_file_name[0].lower())
        sound_url = f'https://media.merriam-webster.com/audio/prons/en/us/mp3/{sound_dir}/{sound_file_name}.mp3'

    return "\n".join(definitions), sound_url

if __name__ == "__main__":
    # Allow command line argument for the word
    if len(sys.argv) > 1:
        search_word = sys.argv[1]
    else:
        search_word = 'vegetable' # Default word

    result_string, sound_url = get_short_definition(search_word)
    
    print(f"\n--- Short Definitions for '{search_word}' ---")
    if result_string:
        print(result_string)
    else:
        print("No definitions found.")
        
    print(f"\n--- Pronunciation URL ---")
    if sound_url:
        print(sound_url)
    else:
        print("No pronunciation found.")
