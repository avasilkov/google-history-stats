"""
author : http://vk.com/blahblahblahnya
"""

import json
import os
from collections import defaultdict
import html.parser

def load_history_file(fn):
    return json.load(open(fn, 'r'))['event']

def load_all_files(path, files):
    data = []
    for f in files:
        data.append(load_history_file(path + f))

    return data

def parse_html_codes(data):
    h = html.parser.HTMLParser()
    for f in data:
        for query in f:
            query['query']['query_text'] = h.unescape(query['query']['query_text'])

    return data

def get_words_dictionary(parsed_data):

    all_words = defaultdict(int)

    for f in parsed_data:
        parsed_words = []
        for query in f:
            parsed_words += (query['query']['query_text']).split()
        for w in parsed_words:
            all_words[w] += 1

    return all_words

path = '../Searches/'

files = os.listdir(path)

data = parse_html_codes(load_all_files(path, files))

all_words = get_words_dictionary(data)


print('Number of different words: %s' % len(all_words))
sorted_keys = sorted(all_words, key=all_words.get)

print('Top 20 words:')
for key in reversed(sorted_keys[-20:]):
    print('%s - %d' % (key, all_words[key]))
