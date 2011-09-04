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
ʣ��쥭�������Х�����ץȡ�

���Υ�����ץȤ�
http://gensen.dl.itc.u-tokyo.ac.jp/
�ǾҲ𤵤�Ƥ��롢���르�ꥺ��ΰ�ĤǤ���FLRˡ�����������ΤǤ���

�ܺ٤ϡ���ʸ
 * ����͵�֡���ä§�����ܹɾ�: "�и����٤�Ϣ�����٤˴�Ť������Ѹ����",�������������Vol.10 No.1, pp. 27 - 45, 2003ǯ1��
    http://www.r.dl.itc.u-tokyo.ac.jp/~nakagawa/academic-res/jnlp10-1.pdf
�򻲾Ȥ��Ƥ���������

���Τ褦�ʤ��Ф餷���������̤�������Ƥ������������˴��դ��Ƥ���ޤ���
"""

#̵�뤹���ʻ�ID
_MUSHI_POSID = set([
    48, 53,   #�����Ƚ����졣����������˽������Ƥ�����Τ�������
    58, 59, 60, 61, 63, 64, 65, 66, 67, 68])

_STOP_WORD = set(["."])

def _filterWord(node):
    if node.posid < 36:
        return False
    if node.posid in _MUSHI_POSID:
        return False
    if node.surface in _STOP_WORD:
        return False
    if node.feature.startswith("̾��"):
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
    ʣ��쥹������׻����ޤ���

    ����:
    stream ���ϥ��ȥ꡼�ࡣʸ����Υ����ͥ졼��������ꤷ�ޤ���(file���֥������Ȥ�sys.stdin��)
    opt   MeCab�������ˤ錄�����ץ����ʸ����
    filterWord MeCab��node������ˤȤꡢ����node��ñ��Ȥ��ƻȤ��ʤ�True���֤�ñ��ե��륿���ؿ������ʤ�ǥե���Ȥ��Ѱդ���Ƥ����Τ�Ȥ��ޤ���
    filterPhras MeCab��node���������ˤȤꡢ����node�����ʣ������Ȥ��ƻȤ��ʤ�True���֤�ñ����ե��륿���ؿ������ʤ�ǥե���Ȥ��Ѱդ���Ƥ����Τ�Ȥ��ޤ���

    �֤���:
    { (ñ��,ñ��,,,) : ʣ��쥹����, ...}
    �η�����dictionary���֥������ȡ�
    ����(ñ��,ñ��,,,)����ʣ����ɽ���ޤ���
    """
    if opt:
        option = opt
    else:
        option = ""

    tagger =MeCab.Tagger(option)

    data = []

    #���ϥǡ�������
    for line in stream:
        data.append(line)

    wordsTF = {}
    wordSet = set()

    #ʬ�����񤭤���ñ�����������٤�׻���
    node = tagger.parseToNode("\n".join(data))
    for word in _wordIter(node, filterWord, filterPhrase):
        word = tuple(map(lambda x: x.surface, word))
        map(wordSet.add, word)
        
        if word in wordsTF:
            wordsTF[word] += 1
        else:
            wordsTF[word] = 1

    #Ϣ�ܿ��׻� 1 : �ޤ���ñ�줴�Ȥˡ���ñ�졢��ñ��ν�����롣
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

    #Ϣ�ܿ��׻� 2 : ��ñ�졢��ñ��ν���Υ������򽸷ס�
    leftNum = defaultdict(int)
    rightNum = defaultdict(int)
    for w in leftSet.keys():
        leftNum[w] = len(leftSet[w])
    for w in rightSet.keys():
        rightNum[w] = len(rightSet[w])

    #����������
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
   ʸ�Ϥ���ʣ���ñ�̤ǽ��ץ�����ɤ���Ф��롣
   ���Ϥ�ɸ�����Ϥ���EUC�����Ϥ��ޤ���
   """)
   parser.add_option("-o", "--opt", dest="opt", help=u"Mecab���ޥ�ɥ饤��ˤ錄�����ץ����", default=None)
   (options, args) = parser.parse_args()

   score = calc(sys.stdin, opt=options.opt)

   for word in score.keys():
       print " ".join(word) + "\t%f" % score[word]
       

