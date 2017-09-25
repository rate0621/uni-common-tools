import sys
import urllib.request
import json
import math
import pandas as pd

import ChunithmNet


class ScoreCalculator:
  def __init__(self, name, password):
    self.cn = ChunithmNet.ChunithmNet(name, password)


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

  def create_baserate_list(self):
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


  def calc_rate(self, baserate_list, score):
    """
    scoreにrateを追加する
    """

    #まずbest枠のrateを算出する
    for key in score:
      score[key]["rate"] = 0
      if score[key]["score"] == 0:
        print (score[key]["music_name"] + " is not play...")
      else:
        if baserate_list[key]["value"] == None:
          print ("Sorry, " + score[key]["music_name"] + " baserate is None.")
        else:
          rate = self.score_to_rate(int(score[key]["score"].replace(',', '')), baserate_list[key]["value"])
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
    score = self.cn.get_score_only()

    return score
    
if __name__ == '__main__':
  args = sys.argv
  sc = ScoreCalculator(args[1], args[2])
  baserate_list = sc.create_baserate_list()
  print (sc.get_best_music_list())

  #cn = ChunithmNet.ChunithmNet(args[1], args[2])

  # TODO:scoreとplaylogはselfで持たせたほうがいい気がする
  #score = cn.get_score_only()
  #score = sc.calc_rate(baserate_list, score)
  #print (sc.calc_finally_rate(score))


