#!/usr/bin/env python
#coding=utf-8
import MeCab
import sys

def isanagram(text):
    for i in range(len(text)/2):
        if text[i] != text[len(text)-i-1]:
            return False
        return True

if __name__ == '__main__':

    mecab = MeCab.Tagger('-Oyomi')
    for line in sys.stdin:
        text = mecab.parse(line)
        text = text.strip().decode('utf-8')
        if len(text) > 3 and isanagram(text):
            print line,
            print u"回文だよ!"
