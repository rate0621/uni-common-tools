import urllib.request
import json

header = "music_id\tdifficulty_id\tmusic_name\tvalue\tlevel\timg_filename\n"



with urllib.request.urlopen("https://chuniviewer.net/api/GetMusicConstantValues.php") as res:
  html = res.read().decode("utf-8")
  ratelist_json = json.loads(html)


f = open('baserate.tsv', 'w')
f.write(header)
baserate_list = {}
for music_info in ratelist_json:
  key = str(music_info["music_id"]) + "_" + str(music_info["difficulty_id"])
  baserate_list[key] = music_info

  f.write(str(music_info['music_id']) + "\t" + str(music_info['difficulty_id']) + "\t" + str(music_info['music_name']) + "\t" + str(music_info['value']) + "\t" + str(music_info['level']) + "\t" + '' + "\n")


f.close()
