# WebApp dev on Minikube

## 概要
- flaskを使って、簡単なWebアプリケーションを作成してみる。
  1. (sample01) とりあえずKubernetes上にコンテナを稼働させる。
  1. (sample02) Flaskを稼働させる。
  1. (sample03) ElasticsearchのデータをFlaskで作成したWEB画面より検索する。
- Windows + Minikube環境上に構築する。

## 構成
| 項目           | バージョン |
|:---------------|:----------|
| Windows        | 10        |
| VirtualBox     | 6.0.4     |
| Vagrant        | 2.2.4     |
| Minikube       | 0.34.1    |
| Kubernetes-cli | 1.13.4    |
| docker-cli     | 18.09.0   |

## Minikube環境準備（sample01）
### 必要なソフトウェアのインストール
[chocolatey](https://chocolatey.org/)を使用します。  
docker-cliはminikubeに内包されているのでminikubeのVMに入れば使用できるけれど、Windows上からも直接、実行できると便利なので導入する。

    choco install virtualbox
    choco install vagrant
    choco install minikube
    choco install kubernetes-cli
    choco install docker-cli

### Minikube環境の起動
minikubeを起動する。

    minikube start

起動を確認する。  
minikube dashboardでブラウザ経由で管理画面が確認できる。

    kubectl cluster-info
    kubectl get node
    minikube dashboard

### サービス起動確認
試しにnginx+redisのpodsを作成する。  
使用するマニフェストは[sample01配下のもの](sample01/webapp-deployment.yml)を使用する。

    kubectl apply -f sample01/webapp-deployment.yml

接続確認する。  
ブラウザが起動して、nginx画面が表示されればOK。

    minikube service webapp

作成したpods(nginx+redis)を削除する。  
ただ公式のnginxおよびredisコンテナを起動させてみただけで、いまのところ使用しない。

    kubectl delete -f sample01/webapp-deployment.yml

## Flask環境の構築（sample02）
### ローカル環境上にubuntu+flaskのイメージを作成
minikube VM上のdockerを使用するように設定する。（PowerShell）

    minikube docker-env --shell powershell | Invoke-Expression
    docker -v

ubuntu+flaskのDockerfileを作成する。  
なお、作成したタイミングによってバージョンが異なることを避けるためには、バージョン指定した方が良い。今回はお試しなので、latestのままとする。

```
FROM ubuntu:latest

RUN apt-get update
RUN apt-get install python3 python3-pip -y

RUN pip3 install flask
COPY webapp_flask.py /
```

ビルドする。

    docker build sample02/. -t local/flask:1.0
    docker images

### minikube上にデプロイ
kubernetes上にデプロイする。  
使用するマニフェストは[sample02配下のもの](sample02/webapp-flask.yml)を使用する。

    kubectl apply -f sample02/webapp-flask.yml
    kubectl get deployments

アクセス確認する。

    curl $(minikube service webapp-flask --url)

作成したリソースを削除する。

    kubectl delete -f sample02/webapp-flask.yml


## Elasticsearchの簡易WEBインターフェース作成（sample03）
もともとこれを作成してみたかった。

### flaskによる簡易フォームの作成
ロジックプログラムは以下のように作成してみた。  
- 動作確認も兼ねて、トップページはHello worldを表示しておく。
- /searchへアクセスするとelasticsearchの検索フォームを表示する。
- Flaskは初めてということもあり、この書き方が良いやり方かは不明だが、動いてはいる。
    - 最初のアクセス時など、GETの場合にはElasticsearchに検索せずに、検索フォームを表示する。
    - 検索フォームでaccount_numberが入力された際には、バックエンドのElasticsearchに検索クエリを投げて、結果を表示する。
    - 本格的に使用するには、セキュリティや例外処理などをもっときちんとする必要あり。
- はまった点は後述…。（改行コードに注意）

```python:webapp_flask_elasticsearch.py
#!/usr/bin/python3
from flask import Flask, render_template, url_for, request
from elasticsearch import Elasticsearch

dest_hostname = 'elasticsearch'

app = Flask(__name__)
es = Elasticsearch([dest_hostname])

@app.route('/')
def index():
  msg = "Hello world!!\n" + "Access " + url_for('search') + " for elasticsearch demo"
  return msg

@app.route('/search', methods=["GET", "POST"])
def search():
  if request.method == "GET":
    hits = []
  if request.method == 'POST':
    account_number = request.form['account_number']
    if account_number is '':
      hits = []
    else:
      body = {
        "query": {
          "term": {
            "account_number": account_number
          }
        }
      }
      res = es.search(index="bank", body=body)
      hits = [dict(list(doc['_source'].items())) for doc in res['hits']['hits']]
  return render_template('search.html', search_results=hits)

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000, debug=True)
```

テンプレートHTMLファイルは以下とした。できるだけシンプルに。
```HTML:search.html
<!DOCTYPE html>
<html lang="ja">
    <head>
       <meta charset="utf-8">
       <title>webapp_flask_elasticsearch</title>
   </head>
    <body>
      <h1>Search for Account Details</h1>
      <form action="{{ url_for('search') }}" method="POST">
        Account Number:
        <input type="text" name="account_number">
        <input type="submit" value="Submit">
      </form>
      <table border="1">
          <thead>
              <tr>
                  <th>account_number</th>
                  <th>balance</th>
                  <th>firstname</th>
                  <th>lastname</th>
                  <th>age</th>
                  <th>gender</th>
                  <th>address</th>
                  <th>employer</th>
                  <th>email</th>
                  <th>city</th>
                  <th>state</th>
              </tr>
          </thead>
          <tbody>
              {% for hit in search_results %}
              <tr>
                  <td>{{ hit.account_number }}</td>
                  <td>{{ hit.balance }}</td>
                  <td>{{ hit.firstname }}</td>
                  <td>{{ hit.lastname }}</td>
                  <td>{{ hit.age }}</td>
                  <td>{{ hit.gender }}</td>
                  <td>{{ hit.address }}</td>
                  <td>{{ hit.employer }}</td>
                  <td>{{ hit.email }}</td>
                  <td>{{ hit.city }}</td>
                  <td>{{ hit.state }}</td>
              </tr>
              {% else %}
                  <td>No account found.</td>
              {% endfor %}
          </tbody>
      </table>
    </body>
</html>
```

### Flaskのイメージを更新
minikube VM上のdockerを使用するように設定する。（PowerShell）

    minikube docker-env --shell powershell | Invoke-Expression
    docker -v

Flask環境に加えて、作成したロジックプログラムとHTMLファイルを配置する。

```dockerfile:Dockerfile
FROM ubuntu:latest

RUN apt-get update
RUN apt-get install python3 python3-pip -y
RUN apt-get install curl -y

RUN pip3 install flask elasticsearch
COPY webapp_flask_elasticsearch.py /
COPY templates/ /templates/
ENTRYPOINT ["/usr/bin/python3", "/webapp_flask_elasticsearch.py"]
```

ビルドする。（バージョンを1.1にあげる。）

    docker build sample03/. -t local/flask:1.1
    docker images

### minikube上にデプロイ
デプロイする。  
使用するマニフェストは[sample03配下のもの](sample03/webapp-elasticsearch.yml)を使用する。

    kubectl apply -f sample03/webapp-elasticsearch.yml
    kubectl get deployments

Elasticsearchへ接続確認する。  
Elasticsearch用にLoadBalancerタイプのServiceを作成しているので、外部からアクセス可能となっている。

    kubectl get pods
    Invoke-WebRequest -Method GET $(minikube service elasticsearch --url)
    # Invoke-WebRequestはcurlのPowershell版相当

### Elasticsearchにサンプルデータ投入
Elasticsearchにデータ投入する。  
Elasticsearch内に入っているデータは[公式のサンプルデータ](https://raw.githubusercontent.com/elastic/elasticsearch/master/docs/src/test/resources/accounts.json)（銀行口座のユーザ情報）を使用した。  
本来はPersistentVolumeを作成して、コンテナの外部にデータを保持するべきだが、今回の目的はそこではないので、内部に保持する。

```
kubectl get pods
kubectl exec -it <elasticsearch-xxx> /bin/bash
curl -O "https://raw.githubusercontent.com/elastic/elasticsearch/master/docs/src/test/resources/accounts.json"
curl -H "Content-Type: application/json" -XPOST 'localhost:9200/bank/account/_bulk?pretty&refresh' --data-binary "@accounts.json"
```

投入したデータを確認する。

    curl -H 'Content-Type: application/json' -XGET "http://localhost:9200/bank/_search?pretty"

ElasticsearchのPodから抜ける。

    exit

### flask上のWEBアプリから検索
ブラウザでアクセスする。

    minikube service webapp-flask

URL末尾にsearchを追加してアクセスし、入力フォームにAccount Number(0から999)を入れて詳細データが表示されることを確認する。

## はまった点
- sample03を作成していた時、コンテナ起動時に以下エラーが出力されてはまった。WindowsのVisualStudioCodeで開発していたので、改行コードがCRLFになっていたことが原因だった。

    FileNotFoundError: [Errno 2] No such file or directory