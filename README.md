uni-common-tools
=====

## 下記ツールたちが利用する共通のライブラリ

* uni-bot
* uni-calc-rater

## 使い方
基本的にサブモジュールとして各ツール配下にcloneする。  
このため、 `requirements.txt` は等リポジトリでは管理せずに、各ツールの `requirements.txt` に記載させる。  

### clone時の注意
便宜上、uni-common-toolsという名前で作成しているが、親プロジェクトからimportするときにハイフンは使えない。  
そのためサブモジュールとしてcloneする際には、
`git submodule add https://github.com/rate0621/uni-common-tools.git uni_common_tools`
と言った形でアンダーバー等のディレクトリ名でcloneしてくること

```
beautifulsoup4==4.6.0
bs4==0.0.1
numpy==1.13.1
pandas==0.20.3
pycrypto==2.6.1
python-dateutil==2.6.1
pytz==2017.2
Simple-AES-Cipher==1.0.6
six==1.11.0
wheel==0.25.0
```
