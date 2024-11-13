import requests
from bs4 import BeautifulSoup

word = 'vegetable'
word = word.replace(' ', '%20')

# my_html = requests.get(f'https://www.merriam-webster.com/dictionary/{word}').content
# print(my_html)
# soup = BeautifulSoup(my_html, 'html.parser')

# bb = soup.find_all('span', attrs= {'class':['sub-content-thread', 'ex-sent', 'sents']})
# print(bb)
# for result in bb:
#     new_result = result.findChild('span', attrs = {'class': ['d-block', 'thread-anchor-content']}, recursive = True)
#     new_result_2 = result.findChild('span', attrs = {'class': ['t', 'has-aq']}, recursive = True)
#     if new_result_2:

#         to_replace_word = new_result_2.findChild('em').text
#         example_sentence = new_result_2.text.replace(to_replace_word,'___ ')
#         print(example_sentence)
    # print(new_result_2)

# print(bb)
# quit()

key = ''
word = 'vegetable'


response = requests.get(f'https://www.dictionaryapi.com/api/v3/references/collegiate/json/{word}?key={key}')
r = response.json()

# print(r)


# print(response.json())

all = r[0]['hwi']['prs'][0]['sound']['audio']
short_def = r[0]
print(all)
# print('\n\n')
# print(all)

# print(short_def)