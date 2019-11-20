# -*- coding:utf-8 -*-

import urllib
import requests
import time
from bs4 import BeautifulSoup
from collections import Counter
import re
import neologdn
import pkg_resources, imp
import spacy
import config

max_page_num = config.max_page_num
top_num = config.top_num
SITE_URL = config.SITE_URL
mstdn_picker_url = config.mstdn_picker_url

print(f"取得する投稿は {max_page_num} セットです。全部で {max_page_num * 40} 投稿です。")
print(f"変更するなら数字を入力してください。変更しないのならEnterを。")


def check_key():
    input_from_key = input("Input int or Enter : ")
    if input_from_key == '':
        print(f"You input Enter\n")
        return max_page_num
    elif str.isdecimal(input_from_key) == True:
        print(f"You input int : {input_from_key}\n")
        return input_from_key
    else:
        print(f"Please input int or Enter\n")
        check_key()

max_page_num = int(check_key())

api_path = SITE_URL + "/api/v1/timelines/public"

session = requests.Session()
since_id = -1
params = {}
if mstdn_picker_url != "":
  url = mstdn_picker_url
  parsed = urllib.parse.urlparse(url)
  query = urllib.parse.parse_qs(parsed.query)
  instance = query.pop("instance", "")
  if isinstance(instance, list):
    instance = instance[0]
  since_id = int(query.get("since_id")[0])
  max_id = int(query.get("max_id")[0])
  params = {"since_id": since_id, "max_id": max_id}
  api_path = SITE_URL + "/api/v1/timelines/public"

params = dict({"local": True, "limit": 40}, **params)
res = session.get(api_path, params=params)

toots = []

DEFAULT_MAX_PAGE_NUM = 50

_max_page_num = DEFAULT_MAX_PAGE_NUM if mstdn_picker_url else max_page_num
print("Toot取得中...", end="")
for i in range(_max_page_num):
  statuses = res.json()
  toots.extend(
      [s["spoiler_text"] + " " + BeautifulSoup(s["content"], "html.parser").text for s in statuses if int(s["id"]) > since_id]
  )
  link_header = requests.utils.parse_header_links(res.headers['Link'].rstrip('>').replace('>,<', ',<'))
  last_toot = res.json()[-1]
  last_id = int(last_toot['id'])
  #print(f"{i}th loop\nThe last toot was created at: {last_toot['created_at']} id: {last_id}")
  print(".", end="")
  next_link = link_header[0]["url"]
  
  if since_id >= last_id:
    break
  res = session.get(next_link)
  time.sleep(1)

print(f"Number of toots: {len(toots)}")

imp.reload(pkg_resources)

nlp = spacy.load('ja_ginza')

CONTENT_WORD_POS = ('名詞')

def remove_url(text):
  return re.sub(r'https?:\/\/.*', '', text)

def extract_words(sentence):
    docs = nlp(sentence)
    words = set(str(w) for w in docs.noun_chunks)
    #for token in docs:
    #    if token.pos_ == "pos:NOUN":
    #        words.append(token.text)

    words.union(str(w) for w in docs.ents)
    return list(words)


def extract_hashtags(sentence):
    return re.findall(r"(#\w+)", sentence, re.MULTILINE)

stop_words = {
    "さん",
    "そう",
    "名前", "今日", "これ", "ここ", "こと", "もの", "ドリキンさん",
    "きた", "やつ", "どこ", "www",
    "ドリキン", "松尾", "感じ", "時間",
    "それ","なん","ため","はず","わけ",
    "お疲れ様", "松尾さん","ところ",
    "自分"
}


print("集計中...")

cnt = Counter()
for t in toots:
    text = remove_url(t)
    #print(text)
    for tag in extract_hashtags(text):
        cnt[tag] +=1

    for w in extract_words(neologdn.normalize(text)):
        #print(f"word: {w} {len(w)}")
        if len(w) <= 1:
            continue
        if w in stop_words:
            continue
        cnt[w] += 1

print("集計完了\n")

"""## 結果発表！！！

以下が、過去800toot中、上位50位（デフォルト値）の名詞です。
話題がなんとなくつかめましたか？
"""

#@title
print(f"Top {top_num} words in past {len(toots)} toots")
print(cnt.most_common(top_num))