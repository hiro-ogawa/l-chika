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

beacon_dict = {
    '01002e6fd4': 'WD0001',
    '01013523b2': 'CH0001',
    '0101372b60': 'VL0001',
    '01013ae20c': 'WD0002',
    '01013aebc1': 'CH0002',
    '01013bc66a': 'VL0002',
    '000001939f': 'CH0003',
    '0000000000': 'WD0004',
}

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
    # print(e.error.message)
    # print(e.error.details)


def send_msgs(msgs, reply_token = None, uid = None, uids = None):
    if not isinstance(msgs, (list, tuple)):
        msgs = [msgs]
    # 各メッセージの不要な改行の削除
    for msg in msgs:
        if msg.type == 'text':
            while msg.text[-1] == '\n':
                msg.text = msg.text[:-1]
    # 空メッセージ削除
    if TextSendMessage('') in msgs:
        msgs.remove(TextSendMessage(''))

    # メッセージがあれば送信
    if len(msgs):
        if len(msgs) > 5:
            try:
                if reply_token:
                    line_bot_api.reply_message(reply_token, msgs[0:5])
                if uid:
                    line_bot_api.push_message(uid, msgs[0:5])
                if uids:
                    line_bot_api.multicast(uids, msgs[0:5])
            except LineBotApiError as e:
                print_error(e)
            print 'len(msgs) > 5'
        else:
            try:
                if reply_token:
                    line_bot_api.reply_message(reply_token, msgs)
                if uid:
                    line_bot_api.push_message(uid, msgs)
                if uids:
                    line_bot_api.multicast(uids, msgs)
            except LineBotApiError as e:
                print_error(e)


@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    _id = event.source.user_id
    reply_msgs = []

    f = open("lchika.json", "r")
    user_dict = json.load(f)
    f.close()
    beacons = user_dict.get(_id,[])

    if(event.message.text[0] == cmd_prefix):
        print('command received')
        cmd = event.message.text[1:]

        if False:
            pass
        elif cmd == u'イルミネーション':
            if len(beacons) == 0:
                reply_msgs.append(TextSendMessage(text=u'Lチカスポットに来てね'))
                send_msgs(reply_msgs, reply_token=event.reply_token)
                return

            reply_msgs.append(TemplateSendMessage(
                alt_text=u'色選択',
                template=CarouselTemplate(
                    columns=[
                        CarouselColumn(
                            # thumbnail_image_url='https://example.com/item1.jpg',
                            # title='this is menu1',
                            text='レインボー',
                            actions=[
                                PostbackTemplateAction(
                                    label='速い',
                                    data=json.dumps({'cmd': 'start_rainbow', 'speed': 10})
                                ),
                                PostbackTemplateAction(
                                    label='遅い',
                                    data=json.dumps({'cmd': 'start_rainbow', 'speed': 2})
                                ),
                                PostbackTemplateAction(
                                    label='止める',
                                    data=json.dumps({'cmd': 'stop_rainbow'})
                                ),
                            ]
                        ),
                        CarouselColumn(
                            # thumbnail_image_url='https://example.com/item1.jpg',
                            # title='this is menu1',
                            text='赤系',
                            actions=[
                                PostbackTemplateAction(
                                    label='赤',
                                    data=json.dumps({'cmd': 'clear', 'color': [255, 0, 0]})
                                ),
                                PostbackTemplateAction(
                                    label='緑っぽい',
                                    data=json.dumps({'cmd': 'clear', 'color': [255, 100, 0]})
                                ),
                                PostbackTemplateAction(
                                    label='青っぽい',
                                    data=json.dumps({'cmd': 'clear', 'color': [255, 0, 100]})
                                ),
                            ]
                        ),
                        CarouselColumn(
                            # thumbnail_image_url='https://example.com/item1.jpg',
                            # title='this is menu1',
                            text='緑系',
                            actions=[
                                PostbackTemplateAction(
                                    label='緑',
                                    data=json.dumps({'cmd': 'clear', 'color': [0, 255, 0]})
                                ),
                                PostbackTemplateAction(
                                    label='赤っぽい',
                                    data=json.dumps({'cmd': 'clear', 'color': [100, 255, 0]})
                                ),
                                PostbackTemplateAction(
                                    label='青っぽい',
                                    data=json.dumps({'cmd': 'clear', 'color': [0, 255, 100]})
                                ),
                            ]
                        ),
                        CarouselColumn(
                            # thumbnail_image_url='https://example.com/item1.jpg',
                            # title='this is menu1',
                            text='青系',
                            actions=[
                                PostbackTemplateAction(
                                    label='青',
                                    data=json.dumps({'cmd': 'clear', 'color': [0, 0, 255]})
                                ),
                                PostbackTemplateAction(
                                    label='赤っぽい',
                                    data=json.dumps({'cmd': 'clear', 'color': [100, 0, 255]})
                                ),
                                PostbackTemplateAction(
                                    label='緑っぽい',
                                    data=json.dumps({'cmd': 'clear', 'color': [0, 100, 255]})
                                ),
                            ]
                        ),
                        CarouselColumn(
                            # thumbnail_image_url='https://example.com/item1.jpg',
                            # title='this is menu1',
                            text='その他',
                            actions=[
                                PostbackTemplateAction(
                                    label='白',
                                    data=json.dumps({'cmd': 'clear', 'color': [255, 255, 255]})
                                ),
                                PostbackTemplateAction(
                                    label='消す',
                                    data=json.dumps({'cmd': 'clear', 'color': [0, 0, 0]})
                                ),
                                PostbackTemplateAction(
                                    label='　',
                                    data=json.dumps({})
                                ),
                            ]
                        ),

                    ]
                )

            ))
        elif cmd == u'サイネージ':
            if len(beacons) == 0:
                reply_msgs.append(TextSendMessage(text=u'Lチカスポットに来てね'))
                send_msgs(reply_msgs, reply_token=event.reply_token)
                return
            reply_msgs.append(TemplateSendMessage(
                alt_text=u'サイネージ（メニュー画面）',
                template=ButtonsTemplate(
                    text=u'どうする？',
                    actions=[
                        PostbackTemplateAction(
                            label=u'音楽を変える',
                            data=json.dumps({'cmd': 'change_music'})
                        ),
                        PostbackTemplateAction(
                            label=u'URLを知りたい',
                            data=json.dumps({'cmd': 'show_sinage_url'})
                        ),
                    ]
                )
            ))
        elif cmd == u'記念撮影':
            if len(beacons) == 0:
                reply_msgs.append(TextSendMessage(text=u'Lチカスポットに来てね'))
                send_msgs(reply_msgs, reply_token=event.reply_token)
                return
            reply_msgs.append(TemplateSendMessage(
                alt_text=u'記念撮影メニュー',
                template=ButtonsTemplate(
                    text=u'どうする？',
                    actions=[
                        PostbackTemplateAction(
                            label=u'写真',
                            data=json.dumps({'cmd': 'take_photo'})
                        ),
                        PostbackTemplateAction(
                            label=u'動画',
                            data=json.dumps({'cmd': 'take_video'})
                        ),
                    ]
                )
            ))

        elif cmd == u'設定':
            reply_msgs.append(TemplateSendMessage(
                alt_text=u'設定メニュー',
                template=ButtonsTemplate(
                    text=u'どうする？',
                    actions=[
                        PostbackTemplateAction(
                            label=u'友達リンク',
                            data=json.dumps({'cmd': 'show_friends_link'})
                        ),
                    ]
                )
            ))

        elif cmd == u'ヘルプ':
            reply_msgs.append(TextSendMessage(text=u'Lチカスポットに行ってテキストを送ってくれるとサイネージに表示するよ！！\n是非いいメッセージを投稿してね！！'))

    else:
        if False:
            pass
        elif event.message.text == u'ビーコン':
            reply_msgs.append(TextSendMessage(text=u'ようこそLチカスポットへ'))
        elif event.message.text == u'カルーセル':
            reply_msgs.append(TemplateSendMessage(
                alt_text=u'AWARDS',
                template=CarouselTemplate(
                    columns=[
                        CarouselColumn(
                            thumbnail_image_url='https://l-chika.herokuapp.com/static/cover.png',
                            # title=u'L-Chikaボット',
                            text=u'みんながLINEで演出家！定点カメラで記念撮影！イルミネーションとデジタルサイネージで作る素敵な時間を共有しよう！！',
                            actions=[
                                URITemplateAction(
                                    label=u'詳細',
                                    uri='https://l-chika-bot.azurewebsites.net/'
                                ),
                            ]
                        ),

                    ]
                )

            ))
            reply_msgs.append(TemplateSendMessage(
                alt_text=u'AWARDS',
                template=CarouselTemplate(
                    columns=[
                        CarouselColumn(
                            text=u'みんながLINEで演出家！定点カメラで記念撮影！イルミネーションとデジタルサイネージで作る素敵な時間を共有しよう！！　みんながLINEで演出家！定点カメラで記念撮影！イルミネーションとデジタルサイネージで作る素敵な時間を共有しよう！！',
                            actions=[
                                URITemplateAction(
                                    label=u'詳細',
                                    uri='https://l-chika-bot.azurewebsites.net/'
                                ),
                            ]
                        ),

                    ]
                )

            ))
            reply_msgs.append(TemplateSendMessage(
                alt_text=u'AWARDS',
                template=CarouselTemplate(
                    columns=[
                        CarouselColumn(
                            thumbnail_image_url='https://l-chika.herokuapp.com/static/cover.png',
                            title=u'L-Chikaボット',
                            text=u'みんながLINEで演出家！イルミネーションとデジタルサイネージで素敵な時間を作ろう！！',
                            actions=[
                                URITemplateAction(
                                    label=u'詳細',
                                    uri='https://l-chika-bot.azurewebsites.net/'
                                ),
                            ]
                        ),

                    ]
                )

            ))
        else:
            ret_np = mapi.negaposi(event.message.text)
            text = u'認識結果：{}\nネガポジ：{}'.format(ret_np["analyzed_text"], ret_np["negaposi"])
            # reply_msgs.append(TextSendMessage(text=text))
            ret_em = mapi.emotion(event.message.text)
            text = u'認識結果：{}\n好嫌：{}\n嬉悲：{}\n怒恐：{}'.format(ret_em["analyzed_text"], ret_em["likedislike"], ret_em["joysad"], ret_em["angerfear"])
            # reply_msgs.append(TextSendMessage(text=text))

            post = False
            if ret_np["negaposi"] < 0 or ret_em["likedislike"] < 0:
                reply_msgs.append(TextSendMessage(text=u"ちょっとネガティブ？"))
            elif ret_np["negaposi"] > 0 or ret_em["likedislike"] > 0:
                reply_msgs.append(TextSendMessage(text=u"いいメッセージだね"))
                post = True
            else:
                post = True

            if post:
                reply_msgs.append(TextSendMessage(text=u"投稿したよ"))
                for hwid in beacons:
                    sinage.PostNewMessage(u"{}：{}".format(event.message.text, line_bot_api.get_profile(event.source.user_id).display_name), beacon_dict.get(hwid, 'ID0001'))

    send_msgs(reply_msgs, reply_token=event.reply_token)

def save_content(message_id, filename):
    message_content = line_bot_api.get_message_content(message_id)
    with open(filename, 'wb') as fd:
        for chunk in message_content.iter_content():
            fd.write(chunk)

@handler.add(MessageEvent, message=ImageMessage)
def handle_image_message(event):
    save_content(event.message.id, 'static/' + event.message.id + '.jpg')
    reply_msgs = []
    reply_msgs.append(TextSendMessage(text=u'画像ありがと'))
    send_msgs(reply_msgs, reply_token=event.reply_token)

@handler.add(MessageEvent, message=VideoMessage)
def handle_video_message(event):
    save_content(event.message.id, 'static/' + event.message.id + '.mp4')
    reply_msgs = []
    reply_msgs.append(TextSendMessage(text=u'動画ありがと'))
    send_msgs(reply_msgs, reply_token=event.reply_token)

@handler.add(MessageEvent, message=AudioMessage)
def handle_audio_message(event):
    save_content(event.message.id, 'static/' + event.message.id + '.m4a')
    reply_msgs = []
    reply_msgs.append(TextSendMessage(text=u'音声ありがと'))
    send_msgs(reply_msgs, reply_token=event.reply_token)

@handler.add(BeaconEvent)
def handle_beacon_message(event):
    _id = event.source.user_id
    reply_msgs = []
    hwid = event.beacon.hwid
    # print 'hwid:{}'.format(hwid)
    print event

    f = open("lchika.json","r")
    user_dict = json.load(f)
    f.close()
    beacons = user_dict.get(_id, [])

    if event.beacon.type == 'enter':
        if hwid not in beacons:
            reply_msgs.append(TextSendMessage(text=u'ようこそLチカスポット{}へ'.format(beacon_dict.get(hwid, 'ID0001'))))
            beacons.append(hwid)

    elif event.beacon.type == 'leave':
        reply_msgs.append(TextSendMessage(text=u'また来てね'))
        if hwid in beacons:
            beacons.remove(hwid)

    send_msgs(reply_msgs, reply_token=event.reply_token)

    user_dict[_id] = beacons
    f = open("lchika.json","w")
    json.dump(user_dict, f)
    f.close()

@handler.add(PostbackEvent)
def handle_postback_message(event):
    _id = event.source.user_id
    reply_msgs = []
    data = json.loads(event.postback.data)
    print data

    f = open("lchika.json", "r")
    user_dict = json.load(f)
    f.close()
    beacons = user_dict.get(_id,[])

    cmd = data.get('cmd')
    if False:
        pass
    elif cmd == 'start_rainbow':
        led.start_rainbow_flow(50, 100, data['speed'])

    elif cmd == 'stop_rainbow':
        led.stop_rainbow_flow()

    elif cmd == 'clear':
        led.clear(50, led.rgb2str([data['color']]))

    elif cmd == 'show_friends_link':
        reply_msgs.append(TextSendMessage(text = u'友達になるためのリンクだよ\nみんなに紹介してね'))
        reply_msgs.append(TextSendMessage(text = line_friend_url))
        img_url = line_qr_url
        reply_msgs.append(ImageSendMessage(original_content_url=img_url, preview_image_url=img_url))

    elif cmd == 'change_music':
        fname = data.get('fname')

        if fname:
            reply_msgs.append(TextSendMessage(text=u'曲を変えたよ'))
            for hwid in beacons:
                sinage.PostNewBGM(fname, beacon_dict.get(hwid, 'ID0001'))

        else:
            reply_msgs.append(TemplateSendMessage(
                alt_text=u'音楽を選ぶ（メニュー画面）',
                template=ButtonsTemplate(
                    text=u'音楽は何がいい？',
                    actions=[
                        PostbackTemplateAction(
                            label=u'ハッピー・クリスマス',
                            data=json.dumps({'cmd': cmd, 'fname': 'happychrismas.mp3'})
                        ),
                        PostbackTemplateAction(
                            label=u'恋人たちのクリスマス',
                            data=json.dumps({'cmd': cmd, 'fname': 'christmas.mp3'})
                        ),
                    ]
                )
            ))
    elif cmd == 'show_sinage_url':
        reply_msgs.append(TextSendMessage(text=u'サイネージのURLはここだよ\n{}'.format(sinage.base_url)))
        for hwid in beacons:
            reply_msgs.append(TextSendMessage(text=u'IDはこれを入れてね\n{}'.format(beacon_dict.get(hwid, 'ID0001'))))

    elif cmd == 'take_photo':
        reply_msgs.append(TextSendMessage(text=u'写真撮ったよ〜'))
        image_url = 'https://l-chika-bot.azurewebsites.net/img/1481447050.jpg'
        reply_msgs.append(ImageSendMessage(
            original_content_url = image_url,
            preview_image_url = image_url,
        ))
        reply_msgs.append(TextSendMessage(text=u'これはIoT x ハードウェアハッカソンでの写真です'))

    elif cmd == 'take_video':
        reply_msgs.append(TextSendMessage(text=u'動画撮ったよ〜'))
        image_url = 'https://l-chika-bot.azurewebsites.net/img/1481447050.jpg'
        reply_msgs.append(ImageSendMessage(
            original_content_url = image_url,
            preview_image_url = image_url,
        ))
        reply_msgs.append(TextSendMessage(text=u'これはIoT x ハードウェアハッカソンでの写真です'))

    # elif event.postback.data == 'bgm:Jhon':
    #     reply_msgs.append(TextSendMessage(text=u'音楽をジョン・レノンのハッピー・クリスマスにするよ'))
    #     sinage.PostNewBGM('happychrismas.mp3')
    # elif event.postback.data == 'bgm:Mariah':
    #     reply_msgs.append(TextSendMessage(text=u'音楽をマライア・キャリーの恋人たちのクリスマスにするよ'))
    #     sinage.PostNewBGM('christmas.mp3')

    send_msgs(reply_msgs, reply_token=event.reply_token)

if __name__ == "__main__":
    app.run(debug=True, port=5002)
