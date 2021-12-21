# coding=utf-8
# Copyright 2018 The Open AI Team Authors and The HuggingFace Inc. team.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from collections import OrderedDict
from typing import List
from ...utils import jieba

class WordpieceTokenizer(object):

    def __init__(self, vocab, unk_token="<unk>", max_input_chars_per_word=200):
        self.vocab = vocab
        self.unk_token = unk_token
        self.max_input_chars_per_word = max_input_chars_per_word

    def tokenize(self, word) -> List[str]:
        if len(word) > self.max_input_chars_per_word:
            return [self.unk_token]

        start = 0
        sub_tokens = []
        while start < len(word):
            end = len(word)
            cur_substr = None
            while start < end:
                substr = word[start:end]
                if substr in self.vocab:
                    cur_substr = substr
                    break
                end -= 1
            if cur_substr is None:
                sub_tokens.append(self.unk_token)
                start += 1
                continue
            sub_tokens.append(cur_substr)
            start = end

        return sub_tokens


def Q2B(uchar):
    if uchar in ['，', '。', '！', '（', '）', '？', '、', '；', '：']:
        return uchar
    inside_code = ord(uchar)
    if inside_code == 0x3000:
        inside_code = 0x0020
    else:
        inside_code -= 0xfee0
    if inside_code < 0x0020 or inside_code > 0x7e: 
        return uchar
    return chr(inside_code)


def read_vocab(path):
    ret = OrderedDict()
    for line in open(path, "r", encoding="utf-8").readlines():
        word = line.strip()
        if len(word) > 0:
            ret[word] = len(ret)
    return ret

class T5Tokenizer:

    def __init__(self, vocab_path, max_len=None, max_sentinels=190):
        self.max_len = max_len if max_len is not None else int(1e12)
        self.encoder = read_vocab(vocab_path)
        self.decoder = {v:k for k,v in self.encoder.items()}
        self.wordpiece_tokenizer = WordpieceTokenizer(vocab=self.encoder)

        self.translator_enc = str.maketrans(" \n", "\u2582\u2583")
        self.translator_dec = str.maketrans("\u2582\u2583", " \n")

        self.sentinel_list = [self.encoder['<s_{}>'.format(i)] for i in range(max_sentinels)]

    @property
    def vocab_size(self):
        return len(self.encoder)

    def __len__(self):
        return len(self.encoder)
    
    @property
    def sod_token(self):
        return "<s>"

    @property
    def eod_token(self):
        return '<eod>'
    
    @property
    def unk_token(self):
        return "<unk>"
        
    @property
    def sod_id(self) -> int:
        return self.encoder[self.sod_token]

    @property
    def eod_id(self):
        return self.encoder[self.eod_token]
    
    @property
    def unk_id(self):
        return self.encoder[self.unk_token]

    def tokenize(self, text : str) -> List[str]:
        """ Tokenize a string. """
        text = ''.join([Q2B(x) for x in text])
        output_tokens = []
        for x in jieba.cut(text, cut_all=False):
            x = x.translate(self.translator_enc)
            output_tokens.extend(self.wordpiece_tokenizer.tokenize(x))
        return output_tokens

    def encode(self, text : str) -> List[int]:
        return self.convert_tokens_to_ids( self.tokenize(text) )

    def decode(self, tokens : List[int]) -> str:
        text = ''.join([self.decoder[x] for x in tokens])
        text = text.translate(self.translator_dec)
        return text

    def convert_tokens_to_ids(self, tokens : List[str]) -> List[int]:
        return [self.encoder.get(x, self.unk_id) for x in tokens]

    def convert_ids_to_tokens(self, ids : List[int]) -> List[str]:
        return [self.decoder[x] for x in ids]
    
    def get_span(self, span_id) -> int:
        return self.encoder["<s_%d>" % span_id]