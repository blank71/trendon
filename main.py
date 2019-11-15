"""
Fork form https://colab.research.google.com/drive/1kWvx8pIVPc6D6TyAwHWjk7nnZolX4VrU
"""
"""
#@title
!apt-get install -y -q sudo file mecab libmecab-dev mecab-ipadic-utf8 git curl python-mecab fonts-ipaexfont fonts-ipafont-gothic
!git clone --depth 1 https://github.com/neologd/mecab-ipadic-neologd.git
!echo yes | mecab-ipadic-neologd/bin/install-mecab-ipadic-neologd -n
!pip install -q natto-py neologdn
!pip install -q mastodon.py beautifulsoup4
!echo `mecab-config --dicdir`"/mecab-ipadic-neologd"
"""
"""## 設定をする

以下のセルでは、2つの設定パラメータがあります
- `max_page_num`: 過去どれだけのtootまで遡るか。 1回 public timeline 40 toot取るので、40 * max_page_num 分のtootを取得します。
- `top_num`: 単語を集計後、上位何位まで表示するかです。デフォルト50位まで表示します。
"""

#@title 設定項目
# どれだけ過去のtootまで遡るか。 max_page_num * 40 toot分取得します
max_page_num = 1 #@param {type:"slider", min:10, max:100, step:10}

# 高頻度語のうち上位いくつの単語を表示するか。デフォルト50です。
top_num = 10 #@param {type:"slider", min:10, max:100, step:1}

"""## 以下はするーっと実行してください

「ランタイム」→「以降のセルを実行」で何も考えずに実行してください。
ただし、連打をするとAPI叩きまくってドリキンさんとさくらさんにご迷惑がかかるかもしれないので、常識の範囲内で...。
"""

#@title
import requests

api_path = "https://mstdn.guru/api/v1/timelines/public"

session = requests.Session()
res = session.get(api_path, params={"local": True, "limit": 40})

#@title
import time
from bs4 import BeautifulSoup

toots = []

for i in range(0, max_page_num):
  statuses = res.json()
  toots.extend([s["spoiler_text"] + " " + BeautifulSoup(s["content"], "html.parser").text for s in statuses])
  link_header = requests.utils.parse_header_links(res.headers['Link'].rstrip('>').replace('>,<', ',<'))
  print(f"{i+1}th loop\nThe last toot was created at: {res.json()[-1]['created_at']}")
  next_link = link_header[0]["url"]
  res = session.get(next_link)
  time.sleep(1)

#@title
len(toots)

#@title
from collections import Counter
from natto import MeCab
import neologdn

import re


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

stop_words = {
  "さん", "そう", "名前", "今日", "これ", "ここ", "きた", "やつ", "どこ", "www"
}

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

"""## 結果発表！！！

以下が、過去800toot中、上位50位（デフォルト値）の名詞です。
話題がなんとなくつかめましたか？
"""

#@title
print(f"Top {top_num} words in past {max_page_num * 40} toots")
print(cnt.most_common(top_num))