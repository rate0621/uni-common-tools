import urllib.request
from urllib.parse import urlencode
import http.cookiejar
import sys, os
from bs4 import BeautifulSoup
import re, pprint

import json
import pandas as pd


class ChunithmNet:
  def __init__(self,name,password):
    def __login():
      login_url = "https://chunithm-net.com/mobile/"
      login_post = {
        'segaId': self.name,
        'password': self.password,
        'save_cookie': "on",
        'sega_login': "sega_login"
      }
      data = urllib.parse.urlencode(login_post).encode("utf-8")

      req = urllib.request.Request(login_url, None, self.headers)
      with urllib.request.urlopen(req, data=data) as res:
        res.close()

      # login画面の先のaime選択画面の突破
      aime_url = "https://chunithm-net.com/mobile/AimeList.html"
      aime_post = {
        'aimeIndex': "0",
        'aimelogin': "aimelogin",
        'aime_login_0': "aime_login_0"
      }
      data = urllib.parse.urlencode(aime_post).encode("utf-8")

      req = urllib.request.Request(aime_url, None, self.headers)
      with urllib.request.urlopen(req, data=data) as res:
        res.close()

    def __create_baserate_list():
      """
      楽曲の譜面定数のリストを返すメソッド
      TODO: ソース上、https://chuniviewer.net/api/GetMusicConstantValues.phpから取ってきているが、
      ゆくゆくはapexに全データを投入し（逐次される仕組みも作る）そこから引っ張るようにする
      """
      with urllib.request.urlopen("https://chuniviewer.net/api/GetMusicConstantValues.php") as res:
        html = res.read().decode("utf-8")
        ratelist_json = json.loads(html)

      ## 負荷軽減のため
      ## {
      ##   key1: {aaa: "hoge", bbb: "weei"},
      ##   key2: {aaa: "huge", bbb: "fooo"}
      ## }
      ## の形式になるように整形
      baserate_list = {}
      for music_info in ratelist_json:
        key = str(music_info["music_id"]) + "_" + str(music_info["difficulty_id"])
        baserate_list[key] = music_info

      return baserate_list

    self.name = name
    self.password = password
    self.baserate_list = __create_baserate_list()

    self.cookiefile = "cookies.txt"
    self.cj = http.cookiejar.LWPCookieJar()
    if os.path.exists(self.cookiefile):
        self.cj.load(self.cookiefile)
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.cj))
    urllib.request.install_opener(opener)

    self.headers = {
      "Accept" :"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
      "Accept-Encoding" :"gzip, deflate, br",
      "Accept-Language" :"ja,en-US;q=0.8,en;q=0.6",
      "Cache-Control" :"max-age=0",
      "Connection" :"keep-alive",
      "Content-Length" :"70",
      "Content-Type" :"application/x-www-form-urlencoded"
    }

    __login()


  def get_score(self):
    """
    自分のプレイデータ情報を取得する
    my_records = {
      ${music_id}_${difficulty_id}: { "music_id": 3, "music_name": "hoge", "difficulty_id": "3", "score": 1000 },
      ${music_id}_${difficulty_id}: { "music_id": 3, "music_name": "bell", "difficulty_id": "3", "score": 1001000 }
    }
    のdict形式でmy_recordsを返す
    """
    ## scoreとrecordが混ざっていることに違和感がないこともないけどきにしないことにする


    score_url = "https://chunithm-net.com/mobile/MusicGenre.html"
    get_score_post = {
      'genre': "99",
      'level': "master",
      'music_genre': "music_genre"
    }
    data = urllib.parse.urlencode(get_score_post).encode("utf-8")

    req = urllib.request.Request(score_url, None, self.headers)
    with urllib.request.urlopen(req, data=data) as res:
      html = res.read().decode("utf-8")
      res.close()

    soup = BeautifulSoup(html, "html.parser")
    article = soup.find_all(class_="w388 musiclist_box bg_master")
    my_records = {}
    for a in article:
      music_data = a.find(class_="music_title")
      music_id = re.search('musicId_(\d+)', str(music_data))
      highscore  = a.find(class_="text_b")

      # TODO: とりあえずMASTERのスコアだけをとるため3を直接書いている
      #       いずれはMASTERとEXPERT（もしくは全部）を取ってくるようにする
      key = str(music_id.group(1)) + "_" + "3"
      if highscore is None:
        my_records[key] = {"music_id": music_id.group(1), "music_name": music_data.text, "difficulty_id": "3", "score": 0}
      else:
        my_records[key] = {"music_id": music_id.group(1), "music_name": music_data.text, "difficulty_id": "3", "score": highscore.text}

    return my_records

  def get_playlog(self):

    playlog_url = "https://chunithm-net.com/mobile/Playlog.html"
    with urllib.request.urlopen(playlog_url) as res:
      html = res.read().decode("utf-8")
      res.close()

    soup = BeautifulSoup(html, "html.parser")
    article = soup.find_all(class_="frame02 w400")
    playlogs = []
    for a in article:
      row = {
        "track_number": a.find(class_="play_track_text").text,
        "music_name": a.find(class_="play_musicdata_title").text,
        "score": a.find(class_="play_musicdata_score_text").text.replace('Score：', ''),
        "play_date": a.find(class_="play_datalist_date").text
      }

      playlogs.append(row)


    return playlogs

  def get_playlog_detail(self, num):
    """
    プレイ履歴から更に詳細情報取得
    @param num(int)
    @return detail(dict)
    """
    playlog_detail_url = "https://chunithm-net.com/mobile/Playlog.html"
    post_data = {
      'nextPage': "PlaylogDetail",
      'args': num,
      'pageMove': "pageMove"
    }
    data = urllib.parse.urlencode(post_data).encode("utf-8")

    req = urllib.request.Request(playlog_detail_url, None, self.headers)
    with urllib.request.urlopen(req, data=data) as res:
      html = res.read().decode("utf-8")
      res.close()

    soup = BeautifulSoup(html, "html.parser")
    detail = {
      "play_date"        : soup.find(class_="box_inner01").text,
      "music_title"      : soup.find(class_="play_musicdata_title").text,
      "score"            : soup.find(class_="play_musicdata_score_text").text.replace('Score：', ''),
      "max_combo"        : soup.find(class_="play_musicdata_max_number").text,
      "justice_critical" : soup.find(class_="play_musicdata_judgenumber text_critical").text,
      "justice"          : soup.find(class_="play_musicdata_judgenumber text_justice").text,
      "attack"           : soup.find(class_="play_musicdata_judgenumber text_attack").text,
      "miss"             : soup.find(class_="play_musicdata_judgenumber text_miss").text
    }
    
    return detail

  def get_score_only(self):
    score_data = self.get_score()

    return score_data

  def get_playlog_only(self):
    playlog_data = self.get_playlog()

    return playlog_data

  def get_score_and_playlog(self):
    score_data = self.get_score_only()
    playlog_data = self.get_playlog()

    return score_data, playlog_data

### 以下、元々別だししていた機能

  def score_to_rate(self, score, base_rate):
    if score >= 1007500 :
      rate = base_rate + 2.0
    elif score >= 1005000:
      rate = base_rate + 1.5 + (score - 1005000) * 10 / 50000
    elif score >= 1000000:
      rate = base_rate + 1.0 + (score - 1000000) *  5 / 50000
    elif score >=  975000:
      rate = base_rate + 0.0 + (score -  975000) *  2 / 50000
    elif score >=  950000:
      rate = base_rate - 1.5 + (score -  950000) *  3 / 50000
    elif score >=  925000:
      rate = base_rate - 3.0 + (score -  925000) *  3 / 50000
    elif score >=  900000:
      rate = base_rate - 5.0 + (score -  900000) *  4 / 50000
    else:
      rate = 0

    return math.floor(rate * 100) / 100


  def calc_rate(self, score):
    """
    scoreにrateを追加する
    """

    #まずbest枠のrateを算出する
    for key in score:
      score[key]["rate"] = 0
      if score[key]["score"] == 0:
        print (score[key]["music_name"] + " is not play...")
      else:
        if self.baserate_list[key]["value"] == None:
          print ("Sorry, " + score[key]["music_name"] + " baserate is None.")
        else:
          rate = self.score_to_rate(int(score[key]["score"].replace(',', '')), self.baserate_list[key]["value"])
          score[key]["rate"] = rate


    ### recent枠の対象曲の算出は現状まだロジックがわかっていないため廃止（単純に上位の曲を持ってくるわけではない模様）
    ## 次のrecent枠のrateを算出
    ## playlogだが、playlogのページからはmusic_idが引けなかったため、
    ## score["music_name"]とplaylog["music_name"]とを紐付けて、そこから、score["music_id"]を引っ張り出して、
    ## baserate_listの譜面定数を導き出し、最終的にrateを算出する。
    ## TODO：とわいえ苦肉の策なので、いずれは楽曲のjpgファイルを使って紐付ける仕様にしたい
    #for num, playlog_value in enumerate(playlog):
    #  playlog[num]["rate"] = 0
    #  for key, score_value in score.items():
    #    if playlog_value["music_name"] == score_value["music_name"]:
    #      if baserate_list[key]["value"] == None:
    #        print ("Sorry, " + score[key]["music_name"] + " baserate is None.")
    #      else:
    #        rate = self.score_to_rate(int(playlog_value["score"].replace(',', '')), baserate_list[key]["value"])
    #        playlog[num]["rate"] = rate
    #        break

    return score


  def calc_finally_rate(self, score):
    """
    与えられた変数score, playlogから算出した平均値を返す
    score -> best枠として上位20位の楽曲
    playlog -> recent枠として上位10位の楽曲

    best、recentの30曲のrateの平均値がrateとなる。
    """

    best_music_limit = 30
    rate_array = []
    for i, key in enumerate(sorted(score, key=lambda x:score[x]["rate"], reverse=True)):
      rate_array.append(score[key]["rate"])
      if i == best_music_limit - 1:
        break

    #recent枠のrate算出は現状不可能なので廃止
    #recent_music_limit = 10
    #for i, playlog_value in enumerate(sorted(playlog, key=lambda x:x["rate"], reverse=True)):
    #  rate_array.append(playlog[i]["rate"])
    #  if i == recent_music_limit - 1:
    #    break

    average = sum(rate_array)/len(rate_array)

    return math.floor(average * 100) / 100

  def get_best_music_list(self):
    """
    NETから抜いてきた自分のスコアを元にベスト枠の曲を抽出する
    """
    score = self.get_score_only()
    return score

if __name__ == '__main__':
  args = sys.argv
  cn = ChunithmNet(args[1], args[2])
  print (cn.get_playlog_detail(0))
  #print (cn.get_playlog())
