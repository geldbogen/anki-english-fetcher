import requests
from bs4 import BeautifulSoup

word = 'vegetable'
word = word.replace(' ', '%20')

my_html = requests.get(f'https://www.merriam-webster.com/dictionary/{word}').content
print(my_html)
soup = BeautifulSoup(my_html, 'html.parser')

bb = soup.find_all('span', attrs= {'class':['sub-content-thread', 'ex-sent', 'sents']})
print(bb)
for result in bb:
    new_result = result.findChild('span', attrs = {'class': ['d-block', 'thread-anchor-content']}, recursive = True)
    new_result_2 = result.findChild('span', attrs = {'class': ['t', 'has-aq']}, recursive = True)
    if new_result_2:

        to_replace_word = new_result_2.findChild('em').text
        example_sentence = new_result_2.text.replace(to_replace_word,'___ ')
        print(example_sentence)
    print(new_result_2)

print(bb)
# quit()
print(short_def)

# deepl_api_key = 'f1dde53b-ff5f-4295-b00a-88cfe1f6a376:fx'

# r = requests.post(
#                 url="https://api-free.deepl.com/v2/translate",
#                 data={
#                     'source_lang' : "EN",
#                     "target_lang": "DE",
#                     "auth_key": deepl_api_key,
#                     "text": 'imbecile',
#                 },
#             )
# print(r.json()['translations'][0]['text'])