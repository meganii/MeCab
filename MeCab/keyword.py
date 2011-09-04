#!/usr/bin/python
# coding=utf-8
import MeCab

def extractKeyword(text):
    tagger = MeCab.Tagger('-Ochasen')
    node = tagger.parseToNode(text.encode('utf-8'))
    keywords = []
    while node:
        if node.feature.split(",")[0] == u"名詞".encode('utf-8'):
            keywords.append(node.surface)
        node = node.next

    return keywords

if __name__ == '__main__':
    text = raw_input(u"入力してください:".encode('utf-8'))
    text = unicode(text, 'utf-8')
    keywords = extractKeyword(text)
    for w in keywords:
        print w,
    print 
