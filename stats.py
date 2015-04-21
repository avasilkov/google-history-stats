import json
import os
from collections import defaultdict
import html.parser

def load_history_file(fn):
    return json.load(open(fn, 'r'))['event']
path = './Searches/'

files = os.listdir(path)

all_words = defaultdict(int)
h = html.parser.HTMLParser()
history_f = h.unescape(load_history_file(path + files[0])[9]['query']['query_text'])

for f in files:
    history_f = load_history_file(path + f)
    parsed_words = []
    for query in history_f:
        parsed_words += h.unescape(query['query']['query_text']).split()
    for w in parsed_words:
        all_words[w] += 1

print('Number of different words: %s' % len(all_words))
sorted_keys = sorted(all_words, key=all_words.get)

print('Top 20 words:')
for key in reversed(sorted_keys[-20:]):
    print('%s - %d' % (key, all_words[key]))
