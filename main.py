from flask import Flask, request, abort
import json, time
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
import re
import requests

access_token = 'UoO2C2d5arwHqKkRDKa1SqFCpOT3f8Vjx8MCvq2cGXiwzBz/ghX5AQ/zmaXZhujEA+yLE0Xs83MlEe3vkGbWjqIxupb/Gu3M/GwEgHsHNDm64QVm24qQ7WbgtZp0UVHdnaYg3Yx/g792VFoeSZP1OwdB04t89/1O/w1cDnyilFU='
secret = '8e9c703ac5225df03e5c3c2104d00a6c'

app = Flask(__name__)

@app.route("/callback", methods=['POST'])
def linebot():
    body = request.get_data(as_text=True)
    try:

        json_data = json.loads(body)
        line_bot_api = LineBotApi(access_token)
        handler = WebhookHandler(secret)
        signature = request.headers['X-Line-Signature']
        handler.handle(body, signature)
        msg = json_data['events'][0]['message']["text"]
        reply_token = json_data['events'][0]['replyToken']
        user_id = json_data['events'][0]['source']['userId']  # 取得使用者 ID ( push message 使用 )
        #line_bot_api.reply_message(reply_token,TextSendMessage(msg))
        #print(msg, reply_token)
        #line_bot_api.push_message(user_id,TextSendMessage(text='安安您好！早餐吃了嗎？'))
        #line_bot_api.push_message('U5ccbb03bc03630a200aa42a84c1ef14a',TextSendMessage(text='安安您好！早餐吃了嗎？'))
        #print(json_data)                                      # 印出內容
        #試試看一開始提示用法或用button
        cities = ['基隆市','嘉義市','臺北市','嘉義縣','新北市','臺南市','桃園縣','高雄市','新竹市','屏東縣','新竹縣','臺東縣','苗栗縣','花蓮縣','臺中市','宜蘭縣','彰化縣','澎湖縣','南投縣','金門縣','雲林縣','連江縣']

        if '雷達' in msg or '雲圖' in msg:
            image_message = ImageSendMessage(
            original_content_url='https://cwbopendata.s3.ap-northeast-1.amazonaws.com/MSC/O-A0058-003.png?time.time_ns()',
            preview_image_url='https://cwbopendata.s3.ap-northeast-1.amazonaws.com/MSC/O-A0058-003.png?time.time_ns()'
            )
            line_bot_api.reply_message(reply_token, image_message)
            #reply_image(f'https://cwbopendata.s3.ap-northeast-1.amazonaws.com/MSC/O-A0058-003.png?{time.time_ns()}', reply_token, access_token)
        elif("提醒" in msg):
            line_notify(weather_msg(get("連江縣")))
        elif(msg[:2] == '天氣'):
            city = msg[3:]
            city = city.replace('台','臺')
            if(not (city in cities)):
                line_bot_api.reply_message(reply_token,TextSendMessage(text="查詢格式為: 天氣 縣市"))
            else:
                # line_bot_api.reply_message(reply_token,TextSendMessage(text=weather_msg(get_data(city))))
                res = get_data(city)
                # print(res)
                line_bot_api.reply_message(reply_token, FlexSendMessage(city + '未來3小時天氣預測',res))
        elif(msg == 'IU'):
            FlexMessage = json.load(open('IUcard.json','r',encoding='utf-8'))
            line_bot_api.reply_message(reply_token, FlexSendMessage('IU',FlexMessage))
        elif '選單' in msg or '預報' in msg or '氣溫' in msg or '溫度' in msg or 'weather' in msg:
            line_bot_api.reply_message(reply_token,
                TextSendMessage(text='請選擇您所在縣市',
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(action=MessageAction(label="臺中市", text = weather_msg(get_data("臺中市")))),
                        QuickReplyButton(action=MessageAction(label="臺北市", text = weather_msg(get_data("臺北市")))),
                        QuickReplyButton(action=MessageAction(label="新竹縣", text = weather_msg(get_data("新竹縣")))),
                        QuickReplyButton(action=MessageAction(label="新竹市", text = weather_msg(get_data("新竹市")))),
                        QuickReplyButton(action=MessageAction(label="新北市", text = weather_msg(get_data("新北市")))),
                        QuickReplyButton(action=MessageAction(label="基隆市", text = weather_msg(get_data("基隆市")))),
                        QuickReplyButton(action=MessageAction(label="桃園市", text = weather_msg(get_data("桃園市")))),
                        QuickReplyButton(action=MessageAction(label="苗栗縣", text = weather_msg(get_data("苗栗縣")))),
                        QuickReplyButton(action=MessageAction(label="彰化縣", text = weather_msg(get_data("彰化縣")))),
                        QuickReplyButton(action=MessageAction(label="宜蘭縣", text = weather_msg(get_data("宜蘭縣"))))
                    ])))
            
        #elif '新竹市' in msg:
        #    line_reply(get_data("新竹市"), reply_token, access_token) 
        else:
            line_bot_api.reply_message(reply_token,TextSendMessage(msg + '非關鍵字，請重新輸入'))
            print(msg, reply_token)

        line_notify(weather_msg(get("臺中市")))


    except:
        print('error')                       # 如果發生錯誤，印出 error
    return 'OK'                              # 驗證 Webhook 使用，不能省略


def get_data(city):
    token = "CWB-BC1F669A-C28F-4CD7-9BC4-9D1346FA0415"
    url = 'https://opendata.cwb.gov.tw/api/v1/rest/datastore/F-D0047-089?Authorization=' + token + '&format=JSON&locationName=' + str(city)
    response = requests.get(url)
    # url = "https://opendata.cwb.gov.tw/api/v1/rest/datastore/F-D0047-089"  # url = "https://opendata.cwb.gov.tw/api/v1/rest/datastore/F-C0032-001"
    # params = {
    #     "Authorization": "CWB-BC1F669A-C28F-4CD7-9BC4-9D1346FA0415",
    #     "locationName": "%E8%87%BA%E4%B8%AD%E5%B8%82",
    # }

    # response = requests.get(url, params=params)
    print(response.status_code)

    if response.status_code == 200:
        # print(response.text)
        data = json.loads(response.text)

        location = data["records"]["locations"][0]["location"][0]["locationName"] # 抓地區
        weather_elements = data["records"]["locations"][0]["location"][0]["weatherElement"]

        res = json.load(open('card.json','r',encoding='utf-8'))
        bubble = json.load(open('weatherCard.json','r',encoding='utf-8'))
        # title
        bubble["body"]["contents"][0]["text"] = city + "未來3小時天氣"
        # time
        bubble["body"]["contents"][1]["contents"][0]["text"] = "{} ~ {}".format(weather_elements[6]["time"][0]["startTime"][5:16],weather_elements[6]["time"][0]["endTime"][5:16])
        # weather
        bubble["body"]["contents"][2]["contents"][0]["contents"][1]["text"] = weather_elements[1]["time"][0]["elementValue"][0]["value"]
        # temp
        bubble["body"]["contents"][2]["contents"][1]["contents"][1]["text"] = "{}°C".format(weather_elements[3]["time"][0]["elementValue"][0]["value"])
        # rain
        bubble["body"]["contents"][2]["contents"][2]["contents"][1]["text"] = "{}%".format(weather_elements[7]["time"][0]["elementValue"][0]["value"])
        # comfort
        bubble["body"]["contents"][2]["contents"][3]["contents"][1]["text"] = weather_elements[5]["time"][0]["elementValue"][1]["value"]
        # body_temp
        bubble["body"]["contents"][2]["contents"][4]["contents"][1]["text"] = "{}°C".format(weather_elements[2]["time"][0]["elementValue"][0]["value"])
        res['contents'].append(bubble)
        return res
    else:
        print("Can't get data!")

def get(city):
    token = "CWB-BC1F669A-C28F-4CD7-9BC4-9D1346FA0415"
    url = 'https://opendata.cwb.gov.tw/api/v1/rest/datastore/F-D0047-089?Authorization=' + token + '&format=JSON&locationName=' + str(city)
    response = requests.get(url)
    print(response.status_code)

    if response.status_code == 200:
        # print(response.text)
        data = json.loads(response.text)

        location = data["records"]["locations"][0]["location"][0]["locationName"] # 抓地區
        weather_elements = data["records"]["locations"][0]["location"][0]["weatherElement"]
    
        # # 0600-0900
        start_time = weather_elements[6]["time"][0]["startTime"]
        end_time = weather_elements[6]["time"][0]["endTime"]
        Wx = weather_elements[1]["time"][0]["elementValue"][0]["value"] #天氣現象
        WeatherDescription = weather_elements[6]["time"][0]["elementValue"][0]["value"] #天氣綜合描述
        rain_prob = weather_elements[7]["time"][0]["elementValue"][0]["value"] #降雨機率
        body_tem = weather_elements[2]["time"][0]["elementValue"][0]["value"] #體感溫度
        tem = weather_elements[3]["time"][0]["elementValue"][0]["value"] #溫度
        comfort = weather_elements[5]["time"][0]["elementValue"][1]["value"] #舒適度指數

        # # 0900-1200
        start_time2 = weather_elements[6]["time"][1]["startTime"]
        end_time2 = weather_elements[6]["time"][1]["endTime"]
        Wx2 = weather_elements[1]["time"][1]["elementValue"][0]["value"] #天氣現象
        WeatherDescription2 = weather_elements[6]["time"][1]["elementValue"][0]["value"] #天氣綜合描述
        rain_prob2 = weather_elements[7]["time"][0]["elementValue"][0]["value"] #降雨機率
        body_tem2 = weather_elements[2]["time"][1]["elementValue"][0]["value"] #體感溫度
        tem2 = weather_elements[3]["time"][1]["elementValue"][0]["value"] #溫度
        comfort2 = weather_elements[5]["time"][1]["elementValue"][1]["value"] #舒適度指數

        # # 1200-1500
        start_time3 = weather_elements[6]["time"][2]["startTime"]
        end_time3 = weather_elements[6]["time"][2]["endTime"]
        Wx3 = weather_elements[1]["time"][2]["elementValue"][0]["value"] #天氣現象
        WeatherDescription3 = weather_elements[6]["time"][2]["elementValue"][0]["value"] #天氣綜合描述
        rain_prob3 = weather_elements[7]["time"][1]["elementValue"][0]["value"] #降雨機率
        body_tem3 = weather_elements[2]["time"][2]["elementValue"][0]["value"] #體感溫度
        tem3 = weather_elements[3]["time"][2]["elementValue"][0]["value"] #溫度
        comfort3 = weather_elements[5]["time"][2]["elementValue"][1]["value"] #舒適度指數

        return tuple([location, start_time, end_time, Wx, Wx2, Wx3, tem, tem2, tem3, rain_prob, rain_prob2, rain_prob3, comfort, comfort2, comfort3, start_time2, end_time2, start_time3, end_time3, body_tem, body_tem2, body_tem3])

def weather_msg(data):
    reply_msg = ""

    if len(data) == 0:
        reply_msg += "\n[Error] 無法取得天氣資訊"
    else:
        reply_msg += f"{data[0]} 的天氣:\n(資料以三小時為一單位)\n"
        reply_msg += f"時間: \n{data[1]} ~\n{data[2]}:\n【{data[3]}】\n"
        reply_msg += f"氣溫: {data[6]}°C\n"        
        reply_msg += f"降雨機率: {data[9]}%\n"
        reply_msg += f"體感溫度: {data[19]}°C"  
        reply_msg += f"舒適度:{data[12]}\n---\n"
        reply_msg += f"時間: \n{data[15]} ~\n{data[16]}:\n【{data[4]}】\n"
        reply_msg += f"氣溫: {data[7]}°C\n"
        reply_msg += f"降雨機率: {data[10]}%\n"  
        reply_msg += f"體感溫度: {data[20]}°C  舒適度:{data[13]}\n---\n"
        reply_msg += f"時間: \n{data[17]} ~\n{data[18]}:\n【{data[5]}】\n"
        reply_msg += f"氣溫: {data[8]}°C\n" 
        reply_msg += f"降雨機率: {data[11]}%\n"
        reply_msg += f"體感溫度: {data[21]}°C  舒適度:{data[14]}\n---\n"
        
        if int(data[9]) > 70 or int(data[10]) > 70 or int(data[11]) > 70:
            reply_msg += "\n提醒您，有機會下雨，出門記得帶把傘哦!\n"
        elif int(data[6]) > 33 or int(data[7]) > 33 or int(data[8]) > 33:
            reply_msg += "\n提醒您，今天很熱，外出要小心中暑哦~\n"
        elif int(data[6]) < 10 or int(data[7]) < 10 or int(data[8]) < 10:
            reply_msg += "\n提醒您，今天很冷，記得穿暖一點再出門哦~\n"

    return reply_msg

def line_notify(data):
    token = "98losJL6ybPyhmMJDcengcay64pSGztEc0MWfOgkEz6"  # 法老王的權杖
    
    # line notify所需資料
    line_url = "https://notify-api.line.me/api/notify"
    line_header = {
        "Authorization": 'Bearer ' + token,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    line_data = {
        "message": data
    }
    #line_bot_api.push_message('U5ccbb03bc03630a200aa42a84c1ef14a',TextSendMessage(text='安安您好！早餐吃了嗎？'))

    requests.post(url=line_url, headers=line_header, data=line_data)

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 80))
    app.run(host='0.0.0.0', port=port)