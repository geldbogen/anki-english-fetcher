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
marriam_webster_api_key = config[
    "Petapro API Key (https://rapidapi.com/petapro/api/linguatools-translate)"]

# get key for Marriam Webster
marriam_webster_api_key = config[
    "Marriam Webster API key (https://dictionaryapi.com/)"]

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

# import algorithms as algo
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

    sound_file_name = r
    short_def_list = r[0]['shortdef']
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

    #API 1 - german-english translation
    try:

        url = "https://petapro-translate-v1.p.rapidapi.com/"

        params = {"query": search_string, "langpair": "en-de"}

        headers = {
            'x-rapidapi-host': "petapro-translate-v1.p.rapidapi.com",
            'x-rapidapi-key': marriam_webster_api_key
        }
        r = requests.get(url=url, params=params, headers=headers)
        r = r.json()
        n[german_translation_field] = r[0]["l1_text"]
    except:
        n[german_translation_field] = "_"

    i = 1
    gerstring = ""

    while True:
        try:
            gerstring = gerstring + r[i]["l1_text"] + "<br>"
            i = i + 1
            pass
            if i == 5:
                break
        except:
            break
    n[german_translation_field_alternative] = gerstring

    # API 2 Marriam-Webster more information about the English word
    n[english_definitions_field] = get_stuff_from_marriam_webster(search_string,marriam_webster_api_key)[0]
    n[examples_prepared_field] = get_example_sentence(search_string)[0]
    n[example_sentences_entry] = get_example_sentence(search_string)[1]
    soundurl = get_stuff_from_marriam_webster(search_string,marriam_webster_api_key)[1]
    
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
