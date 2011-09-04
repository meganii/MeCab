#!/usr/bin/python
# _*_ coding: euc_jp _*_

##    Copyright 2007 Hiroshi Ayukawa (email: ayukawa.hiroshi [atmark] gmail.com)
##
##    Licensed under the Apache License, Version 2.0 (the "License");
##    you may not use this file except in compliance with the License.
##    You may obtain a copy of the License at
##
##        http://www.apache.org/licenses/LICENSE-2.0
##
##    Unless required by applicable law or agreed to in writing, software
##    distributed under the License is distributed on an "AS IS" BASIS,
##    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
##    See the License for the specific language governing permissions and
##    limitations under the License.
import sys
from collections import defaultdict

import MeCab

"""
複合語キーワード抽出スクリプト。

このスクリプトは
http://gensen.dl.itc.u-tokyo.ac.jp/
で紹介されている、アルゴリズムの一つであるFLR法を実装したものです。

詳細は、論文
 * 中川裕志、森辰則、湯本紘彰: "出現頻度と連接頻度に基づく専門用語抽出",自然言語処理、Vol.10 No.1, pp. 27 - 45, 2003年1月
    http://www.r.dl.itc.u-tokyo.ac.jp/~nakagawa/academic-res/jnlp10-1.pdf
を参照してください。

このようなすばらしい研究成果を公開していただき本当に感謝しております。
"""

#無視する品詞ID
_MUSHI_POSID = set([
    48, 53,   #数字と助数詞。これを本当に除外していいものか。。。
    58, 59, 60, 61, 63, 64, 65, 66, 67, 68])

_STOP_WORD = set(["."])

def _filterWord(node):
    if node.posid < 36:
        return False
    if node.posid in _MUSHI_POSID:
        return False
    if node.surface in _STOP_WORD:
        return False
    if node.feature.startswith("名詞"):
        return True
    return False

def _wordIter(node, filterWord, filterPhrase):
    wordBuf = []
    while node:
        if filterWord(node):
            wordBuf.append(node)
        else:
            if len(wordBuf) != 0:
                if filterPhrase(wordBuf):
                    yield wordBuf
                wordBuf = []
        node = node.next
    if len(wordBuf) != 0:
        if filterPhrase(wordBuf):
            yield wordBuf
        
def _filterPhrase(nodes):
    return True

def calc(stream, opt=None, filterWord=_filterWord, filterPhrase=_filterPhrase):
    """
    複合語スコアを計算します。

    引数:
    stream 入力ストリーム。文字列のジェネレーターを指定します。(fileオブジェクトやsys.stdin等)
    opt   MeCabタガーにわたすオプション文字列。
    filterWord MeCabのnodeを引数にとり、そのnodeを単語として使うならTrueを返す単語フィルター関数。空ならデフォルトで用意されているものを使います。
    filterPhras MeCabのnode配列を引数にとり、そのnode配列を複合語候補として使うならTrueを返す単語列フィルター関数。空ならデフォルトで用意されているものを使います。

    返り値:
    { (単語,単語,,,) : 複合語スコア, ...}
    の形式のdictionaryオブジェクト。
    キー(単語,単語,,,)が、複合語を表します。
    """
    if opt:
        option = opt
    else:
        option = ""

    tagger =MeCab.Tagger(option)

    data = []

    #入力データ取得
    for line in stream:
        data.append(line)

    wordsTF = {}
    wordSet = set()

    #分かち書きして単語列の列の頻度を計算。
    node = tagger.parseToNode("\n".join(data))
    for word in _wordIter(node, filterWord, filterPhrase):
        word = tuple(map(lambda x: x.surface, word))
        map(wordSet.add, word)
        
        if word in wordsTF:
            wordsTF[word] += 1
        else:
            wordsTF[word] = 1

    #連接数計算 1 : まずは単語ごとに、左単語、右単語の集合を作る。
    leftSet = {}
    rightSet = {}
    for word in wordsTF.keys():
        lenword = len(word)
        for i in range(lenword):
            w = word[i]
            
            if i != 0:
                if not w in leftSet:
                    leftSet[w] = set()
                leftSet[w].add(word[i-1])
            if i != lenword - 1:
                if not w in rightSet:
                    rightSet[w] = set()
                rightSet[w].add(word[i+1])

    #連接数計算 2 : 左単語、右単語の集合のサイズを集計。
    leftNum = defaultdict(int)
    rightNum = defaultdict(int)
    for w in leftSet.keys():
        leftNum[w] = len(leftSet[w])
    for w in rightSet.keys():
        rightNum[w] = len(rightSet[w])

    #スコア集計
    score = defaultdict(float)
    for word in wordsTF.keys():
        p = 1
        for w in word:
            p *= (1 + leftNum[w]) * (1 + rightNum[w])
        p = pow(p, 1 / float(len(word)) / 2.0)
        score[word] = wordsTF[word] * p

    return score

if __name__ == "__main__":
   import optparse
   
   parser = optparse.OptionParser(u"""
   文章から複合語単位で重要キーワードを抽出する。
   入力は標準入力からEUCで入力します。
   """)
   parser.add_option("-o", "--opt", dest="opt", help=u"Mecabコマンドラインにわたすオプション。", default=None)
   (options, args) = parser.parse_args()

   score = calc(sys.stdin, opt=options.opt)

   for word in score.keys():
       print " ".join(word) + "\t%f" % score[word]
       

