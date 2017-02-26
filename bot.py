#!/usr/bin/python
# -*- coding: utf-8 -*-
import traceback
import json
import os
import sys
from flask import Flask, request, abort
from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import *
from datetime import datetime

import led
import sinage
import metadata_api as mapi

app = Flask(__name__)

# 環境変数が見つかればそっちを読む
# 見つからなければjsonファイルを読む
# なければエラー終了
try:
    # 環境変数読み込み
    line_messaging_api_token = os.environ['LINE_MESSAGING_API_TOKEN']
    line_messaging_api_secret = os.environ['LINE_MESSAGING_API_SECRET']
    line_friend_url = os.environ['LINE_FRIEND_URL']
    line_qr_url = os.environ['LINE_QR_URL']
    base_url = os.environ['BOT_BASE_URL']
    led.led_token = os.environ['LED_TOKEN']
    mapi.api_key = os.environ['METADATA_API_KEY']
    sinage.base_url = os.environ['SINAGE_URL']
    print('os.envrion')

except:
    try:
        # load from json
        f = open('../../lchika_dev.json', 'r')
        json_dict = json.load(f)
        f.close

        line_messaging_api_token = json_dict['LINE_MESSAGING_API_TOKEN']
        line_messaging_api_secret = json_dict['LINE_MESSAGING_API_SECRET']
        line_friend_url = json_dict['LINE_FRIEND_URL']
        line_qr_url = json_dict['LINE_QR_URL']
        base_url = json_dict['BOT_BASE_URL']
        led.led_token = json_dict['LED_TOKEN']
        mapi.api_key = json_dict['METADATA_API_KEY']
        sinage.base_url = json_dict['SINAGE_URL']
        print('json')

    except:
        traceback.print_exc()
        print('load config failed')
        sys.exit(-1)
print('load config success')

line_bot_api = LineBotApi(line_messaging_api_token)
handler = WebhookHandler(line_messaging_api_secret)

cmd_prefix = u'▶'

@app.route("/", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


def print_error(e):
    print(e.status_code)
    print(e.error.message)
    print(e.error.details)

def print_profile(user_id):
    try:
        profile = line_bot_api.get_profile(user_id)
        print(profile.display_name)
        print(profile.user_id)
        print(profile.picture_url)
        print(profile.status_message)
    except linebot.LineBotApiError as e:
        print_error(e)


@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    reply_msgs = []
    if(event.message.text[0] == cmd_prefix):
        print('command received')
        cmd = event.message.text[1:]

        if False:
            pass
        elif cmd == u'色を変える':
            reply_msgs.append(TemplateSendMessage(
                alt_text=u'ツリーの光の色を選んでね（メニュー画面）',
                template=ButtonsTemplate(
                    text=u'ツリーの光の色を選んでね',
                    actions=[
                        PostbackTemplateAction(
                            label=u'赤(Red)',
                            data='led:red'
                        ),
                        PostbackTemplateAction(
                            label=u'緑(Green)',
                            data='led:green'
                        ),
                        PostbackTemplateAction(
                            label=u'青(Blue)',
                            data='led:blue'
                        ),
                        PostbackTemplateAction(
                            label=u'レインボー(Rainbow)',
                            data='led:rainbow'
                        ),
                    ]
                )
            ))
        elif cmd == u'サイネージ':
            reply_msgs.append(TemplateSendMessage(
                alt_text=u'サイネージ（メニュー画面）',
                template=ButtonsTemplate(
                    text=u'どうする？',
                    actions=[
                        PostbackTemplateAction(
                            label=u'音楽を変える',
                            data='sinage:chenge_music'
                        ),
                        PostbackTemplateAction(
                            label=u'URLを知りたい',
                            data='sinage:show_url'
                        ),
                    ]
                )
            ))

        elif cmd == u'設定':
            reply_msgs.append(TemplateSendMessage(
                alt_text=u'設定（メニュー画面）',
                template=ButtonsTemplate(
                    text=u'どうする？',
                    actions=[
                        PostbackTemplateAction(
                            label=u'消す',
                            data='led:black'
                        ),
                        PostbackTemplateAction(
                            label=u'友達リンク',
                            data='show:friends_link'
                        ),
                    ]
                )
            ))

        elif cmd == u'ヘルプ':
            reply_msgs.append(TextSendMessage(text=u'ヘルプはまだないよ'))

    else:
        if False:
            pass
        elif event.message.text == u'ビーコン':
            reply_msgs.append(TextSendMessage(text=u'ようこそLチカスポットへ'))
        else:
            ret_np = mapi.negaposi(event.message.text)
            text = u'認識結果：{}\nネガポジ：{}'.format(ret_np["analyzed_text"], ret_np["negaposi"])
            reply_msgs.append(TextSendMessage(text=text))
            ret_em = mapi.emotion(event.message.text)
            text = u'認識結果：{}\n好嫌：{}\n嬉悲：{}\n怒恐：{}'.format(ret_em["analyzed_text"], ret_em["likedislike"], ret_em["joysad"], ret_em["angerfear"])
            reply_msgs.append(TextSendMessage(text=text))

            if ret_np["negaposi"] < 0 or ret_em["likedislike"] < 0:
                reply_msgs.append(TextSendMessage(text=u"あまりいい言葉じゃないみたい"))
            else:
                reply_msgs.append(TextSendMessage(text=u"投稿したよ"))
                sinage.PostNewMessage(u"{}：{}".format(event.message.text, line_bot_api.get_profile(event.source.user_id).display_name))

    if len(reply_msgs):
        line_bot_api.reply_message(event.reply_token, reply_msgs)

def save_content(message_id, filename):
    message_content = line_bot_api.get_message_content(message_id)
    with open(filename, 'wb') as fd:
        for chunk in message_content.iter_content():
            fd.write(chunk)

@handler.add(MessageEvent, message=ImageMessage)
def handle_image_message(event):
    save_content(event.message.id, 'static/' + event.message.id + '.jpg')
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=u'画像ありがと'))

@handler.add(MessageEvent, message=VideoMessage)
def handle_video_message(event):
    save_content(event.message.id, 'static/' + event.message.id + '.mp4')
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=u'動画ありがと'))

@handler.add(MessageEvent, message=AudioMessage)
def handle_audio_message(event):
    save_content(event.message.id, 'static/' + event.message.id + '.m4a')
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=u'音声ありがと'))

@handler.add(BeaconEvent)
def handle_beacon_message(event):
    if event.beacon.type == 'enter':
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=u'ようこそLチカスポットへ'))


    elif event.beacon.type == 'leave':
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=u'また来てね'))

    else:
        pass


@handler.add(PostbackEvent)
def handle_postback_message(event):
    reply_msgs = []
    if event.postback.data == 'led:red':
        reply_msgs.append(TextSendMessage(text=u'ツリーの光を赤にするよ'))
        led.clear(50, led.rgb2str([[255,0,0]]))

    elif event.postback.data == 'led:green':
        reply_msgs.append(TextSendMessage(text=u'ツリーの光を緑にするよ'))
        led.clear(50, led.rgb2str([[0,255,0]]))

    elif event.postback.data == 'led:blue':
        reply_msgs.append(TextSendMessage(text=u'ツリーの光を青にするよ'))
        led.clear(50, led.rgb2str([[0,0,255]]))

    elif event.postback.data == 'led:black':
        reply_msgs.append(TextSendMessage(text=u'ツリーの光を消したよ'))
        led.clear(50, led.rgb2str([[0,0,0]]))

    elif event.postback.data == 'led:rainbow':
        reply_msgs.append(TextSendMessage(text=u'ツリーの光をレインボーに光らせたよ'))
        led.start_rainbow_flow(50, 100, 5)

    elif event.postback.data == 'show:friends_link':
        reply_msgs.append(TextSendMessage(text = u'友達になるためのリンクだよ\nみんなに紹介してね'))
        reply_msgs.append(TextSendMessage(text = line_friend_url))
        img_url = line_qr_url
        msgs.append(ImageSendMessage(original_content_url=img_url, preview_image_url=img_url))

    elif event.postback.data == 'sinage:chenge_music':
        reply_msgs.append(TemplateSendMessage(
            alt_text=u'音楽を選ぶ（メニュー画面）',
            template=ButtonsTemplate(
                text=u'音楽は何がいい？',
                actions=[
                    PostbackTemplateAction(
                        label=u'ハッピー・クリスマス',
                        data='bgm:Jhon'
                    ),
                    PostbackTemplateAction(
                        label=u'恋人たちのクリスマス',
                        data='bgm:Mariah'
                    ),
                ]
            )
        ))
    elif event.postback.data == 'sinage:show_url':
        reply_msgs.append(TextSendMessage(text=u'サイネージのURLはここだよ\n{}'.format(sinage.base_url)))
    elif event.postback.data == 'bgm:Jhon':
        reply_msgs.append(TextSendMessage(text=u'音楽をジョン・レノンのハッピー・クリスマスにするよ'))
        sinage.PostNewBGM('happychrismas.mp3')
    elif event.postback.data == 'bgm:Mariah':
        reply_msgs.append(TextSendMessage(text=u'音楽をマライア・キャリーの恋人たちのクリスマスにするよ'))
        sinage.PostNewBGM('christmas.mp3')

    if len(reply_msgs):
        line_bot_api.reply_message(event.reply_token, reply_msgs)

if __name__ == "__main__":
    app.run(debug=True, port=5002)
