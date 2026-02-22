from json import JSONDecodeError
from aqt import mw
from anki.hooks import addHook
import requests
import os
from sys import platform
from bs4 import BeautifulSoup

global editorWindow

english_field = "english word"
english_definitions_field = "english definition"
pronunciation_field = "pronunciation (sound)"
etymology_field = "etymology"
difficulty_score_field = "difficulty/frequency"
slang_information_field = "slang information"
slang_example_field = "slang example sentences"
slang_url_field = "urbandictionary-url"
example_sentences_entry = "example sentences"
examples_prepared_field = "prepared sentences"
german_translation_field = "german translation"
german_translation_field_alternative = "alternative translations"

# import the addon's config file
config = mw.addonManager.getConfig(__name__)

#get the windows user name
windowsusername = os.getlogin()

# get the windows user name
ankiusername = config["Anki username"]

# get key for ger-eng API
twinword_key = config[
    "Petapro API Key (https://rapidapi.com/petapro/api/linguatools-translate)"]

# get key for Marriam Webster
marriam_webster_api_key = config[
    "Marriam Webster API key (https://dictionaryapi.com/)"]

# get key for DeepL
deepl_api_key = config[
    "DeepL API Key (https://support.deepl.com/hc/en-us/articles/360021200939-DeepL-API-Free)"]

# get key and ID for Oxford API
ox_key = config[
    "Oxford Dictionary API Key (https://developer.oxforddictionaries.com/)"]
ox_id = config[
    "Oxford Dictionary API ID (https://developer.oxforddictionaries.com/)"]



# get UK or US:
if config["UK or US"] == "UK":
    uk_or_us = "en-gb"
else:
    uk_or_us = "en-us"

# get key for twinword API (difficulty)
twinword_key = config[
    "Twinword language scoring API Key (https://rapidapi.com/twinword/api/twinword-text-analysis-bundle)"]

# get key for Urbandictionary API
urban_key = config[
    "Urban Dictionary API Key (https://rapidapi.com/community/api/urban-dictionary)"]

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

def get_deepl_translation(word :str, key: str) -> str:
    
    r = requests.post(
                url="https://api-free.deepl.com/v2/translate",
                data={
                    'source_lang' : "EN",
                    "target_lang": "DE",
                    "auth_key": key,
                    "text": word,
                },
            )
    try:
        return r.json()['translations'][0]['text']
    except:
        return ''

def get_example_sentence(word : str) -> list[str]:

    word = word.replace(' ', '%20')
    my_html = requests.get(f'https://www.merriam-webster.com/dictionary/{word}').content
    soup = BeautifulSoup(my_html, 'html.parser')

    bb = soup.find_all('span', attrs= {'class':['sub-content-thread', 'ex-sent', 'sents']})

    marriam_example_sentence_list = []
    web_example_sentence_list = []

    pure_marriam_example_sentence_list = []
    pure_web_example_sentence_list = []

    for result in bb:
        new_result = result.findChild('span', attrs = {'class': ['d-block', 'thread-anchor-content']}, recursive = True)
        new_result_2 = result.findChild('span', attrs = {'class': ['t', 'has-aq']}, recursive = True)
        
        if new_result:
            to_replace_word = new_result.findChild('em').text
            pure_example_sentence = new_result.text
            example_sentence = new_result.text.replace(to_replace_word,'___ ')
            marriam_example_sentence_list += [example_sentence]
            pure_marriam_example_sentence_list += [pure_example_sentence]

        if new_result_2:
            to_replace_word = new_result_2.findChild('em').text
            pure_example_sentence = new_result_2.text
            example_sentence = new_result_2.text.replace(to_replace_word,'___ ')
            web_example_sentence_list += [example_sentence]
            pure_web_example_sentence_list += [pure_example_sentence]

            
    final_string_prepared = ''.join([ex.strip() + '<br><br>' for ex in (marriam_example_sentence_list + web_example_sentence_list)[:3]])
    final_string_pure = ''.join([ex.strip() + '<br><br>' for ex in (pure_marriam_example_sentence_list + pure_web_example_sentence_list)[:3]])

    return [final_string_prepared, final_string_pure]

def get_stuff_from_marriam_webster(word : str, key : str) -> list[str]:
    response = requests.get(f'https://www.dictionaryapi.com/api/v3/references/collegiate/json/{word}?key={key}')
    r = response.json()

    # print(r)


    # print(response.json())

    if not r or isinstance(r[0], str):
        return ["Definition not found", ""]

    sound_file_name = r
    short_def_list = r[0].get('shortdef', [])
    short_def = ''.join([item + '\n' for item in short_def_list])

    try:
        sound_file_name = r[0]['hwi']['prs'][0]['sound']['audio']
    except:
        sound_file_name = 'ERROR'
    sound_file__first_letter = sound_file_name[0].lower()

    sound_url = f'https://media.merriam-webster.com/audio/prons/en/us/mp3/{sound_file__first_letter}/{sound_file_name}.mp3'

    return [short_def, sound_url]


def fill_the_fields(flag):
    global editorWindow
    n = editorWindow.editor.note

    search_string = mw.col.media.strip(n[english_field])

    #API 1 - German-English translation
    
    n[german_translation_field] = get_deepl_translation(search_string, deepl_api_key)

    # API 2 Marriam-Webster more information about the English word
    
    n[english_definitions_field] = get_short_definition(search_string)
    n[examples_prepared_field] = get_example_sentence(search_string)[0]
    n[example_sentences_entry] = get_example_sentence(search_string)[1]
    soundurl = get_pronunciation(search_string)
    
    try:
        url = soundurl
        print(soundurl)
        doc = requests.get(url, headers={'app_id': ox_id, 'app_key': ox_key})
        if platform == 'win64' or platform == 'win32':
            with open(
                    "C:/Users/" + windowsusername + "/AppData/Roaming/Anki2/" +
                    ankiusername + "/collection.media/" + search_string +
                    "_us_1.mp3", "wb") as f:
                f.write(doc.content)
        elif platform == 'darwin':
            filepath = os.path.join('/Users', 'juliusniemeyer', 'Library',
                                    'Application Support', 'Anki2',
                                    ankiusername, 'collection.media',
                                    search_string + '_us_1.mp3')
            with open(filepath, "wb") as f:
                f.write(doc.content)
    except Exception as e:
        n[pronunciation_field] = str(e.args)
    else:
        n[pronunciation_field] = "[sound:" + search_string + "_us_1.mp3]"

    # API 3
    try:
        url = "https://twinword-language-scoring.p.rapidapi.com/word/"

        params = {"entry": search_string}

        headers = {
            'x-rapidapi-key': twinword_key,
            'x-rapidapi-host': "twinword-language-scoring.p.rapidapi.com"
        }
        r = requests.get(url, headers=headers, params=params)
        r = r.json()
        try:
            n[difficulty_score_field] = str(r["ten_degree"])
        except KeyError:
            n[difficulty_score_field] = ""
    except:
        n[difficulty_score_field] = ""
    
    
    # API 4 urban dictionary
    urbanendpoint = "https://mashape-community-urban-dictionary.p.rapidapi.com/define"
    params = {"term": search_string}
    headers = {
        'x-rapidapi-host': 'mashape-community-urban-dictionary.p.rapidapi.com',
        'x-rapidapi-key': urban_key
    }
    r = requests.get(url=urbanendpoint, params=params, headers=headers)
    r = r.json()
    try:
        n[slang_information_field] = str(r["list"][0]["definition"])
    except:
        pass
    try:
        n[slang_example_field] = str(r["list"][0]["example"])
    except:
        pass
    try:
        n[slang_url_field] = str(r["list"][0]["permalink"])
    except:
        pass

    editorWindow.editor.loadNote()


def menu_popup(self, menu):
    global editorWindow
    editorWindow = self
    a = menu.addAction("Fill with English information")
    a.triggered.connect(fill_the_fields)

addHook('EditorWebView.contextMenuEvent', menu_popup)
