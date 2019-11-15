# trendon
fork from https://colab.research.google.com/drive/1kWvx8pIVPc6D6TyAwHWjk7nnZolX4VrU

# 準備
"""
$ apt-get install -y -q sudo file mecab libmecab-dev mecab-ipadic-utf8 git curl python-mecab fonts-ipaexfont fonts-ipafont-gothic
$ git clone --depth 1 https://github.com/neologd/mecab-ipadic-neologd.git
$ echo yes | mecab-ipadic-neologd/bin/install-mecab-ipadic-neologd -n
$ pip install -q natto-py neologdn
$ pip install -q mastodon.py beautifulsoup4
$ echo `mecab-config --dicdir`"/mecab-ipadic-neologd"
"""