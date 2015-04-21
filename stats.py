"""
author : http://vk.com/blahblahblahnya
"""

import json
import os
from collections import defaultdict
import html.parser
import pandas as pd
import datetime as dt
import re

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

def load_date_and_text_from_file(fn):
    h_parser = html.parser.HTMLParser()

    data = load_history_file(fn)
    df = []
    for query in data:
        query_q = query['query']
        usec_int = int(query_q['id'][0]['timestamp_usec'])//1E6
        date = dt.datetime.fromtimestamp(usec_int)
        query_text = h_parser.unescape(query_q['query_text'])
        df.append((date, query_text))

    return df

def load_df_from_file(fn):
    df = load_date_and_text_from_file(fn)
    df = pd.DataFrame.from_records(df)
    df = df.set_index(0)
    df.index.names = ['datetime']
    df.rename(columns={1 : 'text'}, inplace=True)

    return df

def get_words_dictionary_from_df(df):

    all_words = defaultdict(int)

    parsed_words = []
    for query in df['text'].tolist():
        for w in re.split('\W+|_', query):
            all_words[w] += 1

    del all_words['']

    return all_words


df = None

csv_path = 'all_history_in_one_file.csv'

if os.path.exists(csv_path):

    df = pd.read_csv(csv_path, index_col=0, parse_dates=True)

else:

    path = '../Searches/'

    files = os.listdir(path)

    for f in files:
        one_file_df = load_df_from_file(path + f)
        if df is None:
            df = one_file_df
        else:
            df = df.append(one_file_df)
    df.to_csv(csv_path)

all_words = get_words_dictionary_from_df(df)

print('Number of different words: %s' % len(all_words))
sorted_keys = sorted(all_words, key=all_words.get)

print('Top 20 words:')
for key in reversed(sorted_keys[-20:]):
    print('%s - %d' % (key, all_words[key]))

import matplotlib
matplotlib.use('TkAgg') # <-- THIS MAKES IT FAST!
import matplotlib.pyplot as plt
fig = plt.Figure(facecolor='w')
plt.suptitle('Google search history stats')
hours_ax = plt.subplot(111)
by_hours = df.groupby(lambda x: x.hour).size()
hours_ax.bar(by_hours.index.values, by_hours.values, align='center', width=0.8,
             color='#99ccff', edgecolor='#99ccff')
hours_ax.set_xticks(by_hours.index.values)
hours_ax.set_xlim([-0.5, 23.5])
hours_ax.set_title('Hourly search activity')

plt.show()
