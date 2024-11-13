import requests
from bs4 import BeautifulSoup

word = 'vegetable'
word = word.replace(' ', '%20')

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

            
    final_string_prepared = ''.join([ex.strip() + '\n\n' for ex in (marriam_example_sentence_list + web_example_sentence_list)[:3]])
    final_string_pure = ''.join([ex.strip() + '\n\n' for ex in (pure_marriam_example_sentence_list + pure_web_example_sentence_list)[:3]])

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

if __name__ == '__main__':
    print(get_example_sentence('Renaissance man'))
    print(get_example_sentence('vegetable'))

    