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
from matplotlib.ticker import FuncFormatter
import calendar as cc

fig = plt.figure(facecolor='w', edgecolor='w')
plt.suptitle('Google search history stats')
def add_interval_activity(title, xticks, df, fig_size, plot_size, n, how, xticks_f):
    ax = plt.subplot2grid(fig_size,
                          (n//(fig_size[1]//plot_size[1])*plot_size[0],
                           n%(fig_size[1]//plot_size[1])*plot_size[1]),
                          rowspan=plot_size[0],
                          colspan=plot_size[1], axisbg='w')
    by_interval = df.groupby(how).size()
    ax.bar(by_interval.index.values, by_interval.values, align='center', width=0.8,
                 color='#99ccff', edgecolor='#99ccff')
    ax.set_xticks(by_interval.index.values[::xticks])
    ax.set_xlim([min(by_interval.index.values) -0.5, max(by_interval.index.values) + 0.5])
    ax.xaxis.set_major_formatter(xticks_f)
    ax.set_title(title)

interval_activity = [
                     (lambda x: x.hour, 'Hourly', 2, lambda x, p: x),
                     (lambda x: x.weekday, 'Daily', 1,
                      lambda x, p: cc.day_abbr[x]),
                     (lambda x: x.month, 'Monthly', 2,
                      lambda x, p: cc.month_abbr[x])
                    ]
for i, act in enumerate(interval_activity):
    formatter = FuncFormatter(act[3])
    add_interval_activity('%s search activity' % act[1], act[2], df,
                          (6, 6), (3, 2), i, act[0], formatter)
fig.tight_layout()
plt.show()
