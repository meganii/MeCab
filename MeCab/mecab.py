#!/usr/bin/env python
#encording: utf-8
from MeCab import *
from sys import *

def is_kaibun(text):
    for i in range(len(text)/2):
        if text[i] != text[len(text)-i-1]:
            return False
        return True

if __name__ == '__main__':
    
    tagger = Tagger("-Oyomi")
    for line in stdin:
        yomi = tagger.parse(line)
        yomi = yomi.strip().decode('utf-8')
        if len(yomi) >=4 and is_kaibun(yomi):
            print line,
