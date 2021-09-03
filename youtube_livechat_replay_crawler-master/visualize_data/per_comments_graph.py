import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.dates import DateFormatter,date2num
from collections import Counter
from pandas.io import json
from logging import getLogger
import logging
import os
import csv
import re
from  datetime import datetime
import shutil

logger = getLogger(__name__)
logging.basicConfig(level=logging.INFO)

#絵文字コード削除用データ
emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"
        u"\U0001F300-\U0001F5FF"
        u"\U0001F680-\U0001F6FF"
        u"\U0001F1E0-\U0001F1FF"
        u"\U0001F9E1"
                           "]+", flags=re.UNICODE)

#データ前処理関数
def preprocessing(json_path):
    logger.info("preprocessing data・・・")
    tmp_texts=[]
    std_values={}
    text_times=[]
    tmp_times=[]


    j_file = json_path
    df_json = pd.read_json(j_file, lines=True)
    df1 = df_json.loc[:, ["time", "text"]]

    #マイナス時刻表示を0.00に置換
    df1["time"]=df1["time"].replace('^-.*', '0:00', regex=True)

    #文字列型時刻をdatatime型に変換。
    for time in df1["time"]:
        if len(time) <= 5: 
            time = datetime.strptime(time ,'%M:%S')
        else:
            time = datetime.strptime(time ,'%H:%M:%S')
        tmp_times.append(time)
    df1["time"] = tmp_times
        
    #絵文字データ削除
    for chat_text in df1["text"]:
        chat_text =re.sub(f'(:_?.+:)+', '', chat_text)
        chat_text = emoji_pattern.sub(r'', chat_text)
        tmp_texts.append(chat_text.strip())
    df1["text"]=tmp_texts

    #テキストが空の行を削除。
    df2 =df1[df1["text"] != ""]

     #抽出データCSV出力
    with  open("sample2.csv" ,"w" , newline="", errors="ignore") as f:
        writer = csv.writer(f)
        writer.writerow(["time", "text"])
        for t,t2 in zip(df2["time"], df2["text"]):
            writer.writerow(["{}:{}:{}".format(str(t.hour), str(t.minute).zfill(2), str(t.second).zfill(2)), t2])

    
    #コメント、出現率を取得
    for index, value in df2["text"].value_counts(normalize=True).iteritems():
        std_percent=round(value*100, 2)
        #出現率0.1パーセント以下のコメントは除去
        if std_percent < 0.1:
            continue
        std_values[index] = value
    #コメント毎に時刻を取得

    import time
    #コメント毎に時刻を取得
    for key, _ in std_values.items():
        tmp_df=df2.query(f'text == "{key}"')
        time.sleep(0.1)
        #Counterオブジェクトに変換
        cnt=Counter((tmp_df["time"].tolist()))
        #最頻値順に並び変えてList型(in tuple)に型変換
        text_times.append(cnt)
    
    plot(std_values, text_times)

#データプロット関数
def plot(std_values, text_times):
    logger.info("ploting data・・・")
    import time


    j=1
    for text,text_time in zip(std_values.keys(), text_times):
        time.sleep(1)

        #画像をフルサイズで表示。
        fig = plt.figure()
        fig.set_size_inches(32,18)
        plt.xlabel("時刻")
        plt.ylabel("出現回数")

        #X軸ラベルを270度回転
        plt.xticks(rotation=270)

        plt.gca().get_yaxis().get_major_formatter().set_useOffset(False)
        # Y軸の数字が必ず整数になるようにする
        plt.gca().get_yaxis().set_major_locator(ticker.MaxNLocator(integer=True))
  

        #最大盛り上がり時刻を取得
        text_time_tmp=text_time.most_common(6)    

        #最大盛り上がり時刻をX軸の目盛りに設定
        new_xticks=date2num([s[0].to_datetime64() for s in text_time_tmp])
        plt.gca().get_xaxis().set_major_formatter(DateFormatter('%H:%M:%S'))
        plt.gca().get_xaxis().set_major_locator(ticker.FixedLocator(new_xticks))




        plt.title(text)
        plt.plot(text_time.keys(), text_time.values())
        plt.savefig(f"../images/image{j}.png", bbox_inches="tight")
        j=j+1
        plt.clf()
        plt.close()
    logger.info("Done!")