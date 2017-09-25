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
    self.name = name
    self.password = password

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



  def login(self):
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

  def get_score(self):
    ## scoreとrecordが混ざっていることに違和感がないこともないけどきにしないことにする

    #self.login()

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
        "music_name": a.find(class_="play_musicdata_title").text,
        "score": a.find(class_="play_musicdata_score_text").text.replace('Score：', ''),
        "play_date": a.find(class_="play_datalist_date").text
      }

      playlogs.append(row)


    return playlogs


  def get_score_only(self):
    self.login()
    score_data = self.get_score()

    return score_data

  def get_playlog_only(self):
    self.login()
    playlog_data = self.get_playlog()

    return playlog_data

  def get_score_and_playlog(self):
    self.login()
    score_data = self.get_score_only()
    playlog_data = self.get_playlog()

    return score_data, playlog_data

if __name__ == '__main__':
  args = sys.argv
  cn = ChunithmNet(args[1], args[2])
  #cn.get_score_only()
  print (cn.get_playlog_only())
