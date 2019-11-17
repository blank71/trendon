# -*- coding:utf-8 -*-

import config
import requests
import time
from bs4 import BeautifulSoup
from collections import Counter
from natto import MeCab
import neologdn
import re
import json

max_page_num = config.max_page_num
top_num = config.top_num
SITE_URL = config.SITE_URL

print(f"取得する投稿は {max_page_num} セットです。全部で {max_page_num * 40} 投稿です。")
print(f"変更するなら数字を入力してください。変更しないのならEnterを。")


def check_key():
    input_from_key = input("Input int or Enter : ")
    if input_from_key == '':
        print(f"You input Enter\n")
        return max_page_num
    elif str.isdecimal(input_from_key) == True:
        print(f"You input int : {input_from_key}")
        return input_from_key
    else:
        print(f"Please input int or Enter")
        check_key()

max_page_num = int(check_key())

api_path = SITE_URL + "/api/v1/timelines/public"

session = requests.Session()
res = session.get(api_path, params={"local": True, "limit": 40})



toots = []

for i in range(0, max_page_num):
  statuses = res.json()
  toots.extend([s["spoiler_text"] + " " + BeautifulSoup(s["content"], "html.parser").text for s in statuses])
  link_header = requests.utils.parse_header_links(res.headers['Link'].rstrip('>').replace('>,<', ',<'))
  print(f"{i+1}th loop. The last toot was created at: {res.json()[-1]['created_at']}")
  next_link = link_header[0]["url"]
  res = session.get(next_link)
  time.sleep(1)

len(toots)

CONTENT_WORD_POS = ('名詞')

def remove_url(text):
  return re.sub(r'https?:\/\/.*', '', text)

def extract_words(tagger, sentence):
    words = []
    for line in tagger.parse(sentence).splitlines()[:-1]:
        surface, feature = line.split('\t')
        if feature.startswith(CONTENT_WORD_POS) and ',非自立,' not in feature:
            words.append(surface)
    return words

stop_words = config.stop_words

stop_pattern = r"\d+"

dic_path = "/usr/local/lib/mecab/dic/mecab-ipadic-neologd"
mc = MeCab("-d {}".format(dic_path))

cnt = Counter()
for t in toots:
  for w in extract_words(mc, neologdn.normalize(remove_url(t))):
    if len(w) <= 1:
      continue
    if w in stop_words:
      continue
    if re.match(stop_pattern, w):
      continue
    cnt[w] += 1

print(f"\nTop {top_num} words in past {max_page_num * 40} toots")
print(cnt.most_common(top_num))