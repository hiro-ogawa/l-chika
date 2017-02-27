#!/usr/bin/python
# -*- coding: utf-8 -*-
import requests
import json
import urllib
# import xmltodict
import feedparser
# import xml.etree.ElementTree as ET

'''
高精度ネガポジ API / 感情解析 API / 5w1h API APIキー発行お知らせメール

ご登録手続きありがとうございます。
次のAPIキーをご利用ください。
***************
ご利用回数上限は、3種類のAPI合わせて1日100回です。
(利用形態などにより、上限回数の拡張をご希望の場合、
mextractr@metadata.co.jp まで、APIキーを添えてご相談ください。)

このAPIキーで、下記のURLから呼び出し可能です。
高精度ネガポジ API: http://ap.mextractr.net/ma9/negaposi_analyzer
感情解析 API: http://ap.mextractr.net/ma9/emotion_analyzer

5w1h API: http://ap.mextractr.net/ma9/mext5w1h

*高精度ネガポジ API:
入力パラメータ
http://ap.mextractr.net/ma9/negaposi_analyzer?out=<出力データの形式>&apikey=xxxxx&text=<URLエンコードした文字列>
パラメータ   形式      意味
text    UTF8でURLエンコードした文字列      メタデータ抽出元の文字列
out     出力データの形式：atom | json デフォルトはatom
callback        out=jsonの場合に有効。JSONP形式のを指定
apikey  文字列     APIキー（必須）

*感情解析 API:
入力パラメータ
http://ap.mextractr.net/ma9/emotion_analyzer?out=<出力データの形式>&apikey=xxxxx&text=<URLエンコードした文字列>
パラメータ   形式      意味
text    UTF8でURLエンコードした文字列      メタデータ抽出元の文字列
out     出力データの形式：atom | json デフォルトはatom
callback        out=jsonの場合に有効。JSONP形式のを指定
apikey  文字列     APIキー（必須）
*5w1h API:
入力パラメータ
http://ap.mextractr.net/ma9/mext5w1h?apikey=xxxxx&text=<URLエンコードした文字列>
パラメータ   形式      意味
text    UTF8でURLエンコードした文字列      メタデータ抽出元の文字列
apikey  文字列     APIキー（必須）
'''

base_url = 'http://ap.mextractr.net/ma9'
negaposi_url = base_url + '/negaposi_analyzer'
emotion_url = base_url + '/emotion_analyzer'
mext5w1h_url = base_url + '/mext5w1h'
api_key = ''

def negaposi(text):
    if api_key is None:
        return {}
    payload = {
        'text': text,
        'out': 'json',
        # 'callbck': led_token,
        'apikey': api_key,
    }

    r = requests.get(negaposi_url, params=payload)
    # print r
    # print urllib.unquote(r.content)
    return json.loads(urllib.unquote(r.content))

def emotion(text):
    if api_key is None:
        return {}
    payload = {
        'text': text,
        'out': 'json',
        # 'callbck': led_token,
        'apikey': api_key,
    }

    r = requests.get(emotion_url, params=payload)
    # print r
    # print urllib.unquote(r.content)
    return json.loads(urllib.unquote(r.content))

from pprint import pprint
def mext5w1h(text):
    if api_key is None:
        return {}
    payload = {
        'text': text,
        'apikey': api_key,
    }

    r = requests.get(mext5w1h_url, params=payload)
    # print r.content

    atom = feedparser.parse(r.content)
    # print atom
    pprint(atom)

    # xmldict = dict(xmltodict.parse(r.content))
    # # print xmldict
    # pprint(dict(xmldict["feed"]["entry"]))
    # print(xmldict["feed"]["entry"]["content"])
    # print(xmldict["feed"]["entry"]["summary"])
    # pprint(dict(xmldict["feed"]["entry"]["gd:extendedProperty"]))
    # pprint(dict(xmldict["feed"]["entry"]["gd:when"]))
    # print(xmldict["feed"]["entry"]["gd:where"])
    # root = ET.fromstring(r.content)
    # root = ET.fromstring(r.text.encode('utf-8'))

    # 最上位階層のタグと中身
    # print(root.tag,root.attrib)

    # 子階層のタグと中身
    # for child in root:
    #     print(child.tag, child.attrib, child.text)
    #     for gc in child:
    #         print(gc.tag, gc.attrib, gc.text)

    return r.content


if __name__ == "__main__":
    text = u'お仕事お疲れ様です．帰りに，パックのご飯３つと，牛乳とハーゲンダッツを買ってきてくれると嬉しいな．疲れているところごめんね．'
    text = u'混成チームは、新垣結衣一択でお願いします！'
    text = u'大好き'

    # ret = negaposi(text)
    # print ret["negaposi"]
    # print ret["analyzed_text"]

    # ret = emotion(text)
    # print ret["joysad"]
    # print ret["likedislike"]
    # print ret["angerfear"]
    # print ret["analyzed_text"]

    text = u'来る10月23日、定時株主総会を文京区小石川2-1-2の弊社本店A会議室にて開催いたします。是非ご出席いただけますようお願い申しあげます。 メタデータ株式会社'
    mext5w1h(text)
