import requests
from bs4 import BeautifulSoup
import sys

def get_short_definition(word: str) -> str:
    # Construct the URL
    url = f'https://www.merriam-webster.com/dictionary/{word}'
    print(f"Fetching: {url}")
    
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching page: {e}")
        return ""

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

    return "\n".join(definitions)

if __name__ == "__main__":
    # Allow command line argument for the word
    if len(sys.argv) > 1:
        search_word = sys.argv[1]
    else:
        search_word = 'vegetable' # Default word

    result_string = get_short_definition(search_word)
    
    print(f"\n--- Short Definitions for '{search_word}' ---")
    if result_string:
        print(result_string)
    else:
        print("No definitions found.")
