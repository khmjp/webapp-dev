# WebApp dev on Minikube

## 概要
- ごく簡単なWebアプリケーションを作成してみる
- Windows + Minikube環境上に構築
- ちょっとした開発や確認に。

## 構成
| 項目           | バージョン |
|:---------------|:----------|
| Windows        | 10        |
| VirtualBox     | 6.0.4     |
| Vagrant        | 2.2.4     |
| Minikube       | 0.34.1    |
| Kubernetes-cli | 1.13.4    |
| docker-cli     | 18.09.0   |


## 環境準備
### 必要なソフトウェアのインストール
[chocolatey](https://chocolatey.org/)を使用します。

    choco install virtualbox
    choco install vagrant
    choco install minikube
    choco install kubernetes-cli
    choco install docker-cli

### Minikube環境の起動
minikubeを起動する。

    minikube start

起動を確認する。

    kubectl cluster-info
    kubectl get node
    minikube dashboard

### サービス起動確認
試しにnginx+redisのpodsを作成

    kubectl apply -f sample01/webapp-deployment.yml

接続確認

    minikube service webapp

作成したpods(nginx+redis)を削除

    kubectl delete -f sample01/webapp-deployment.yml


## flask環境の構築
### ローカル環境上にubuntu+flaskのイメージを作成
minikube VM上のdockerを使用するように設定（PowerShell）

    minikube docker-env --shell powershell | Invoke-Expression
    docker -v

ubuntu+flaskのDockerfileを作成

```
FROM ubuntu:latest

RUN apt-get update
RUN apt-get install python3 python3-pip -y

RUN pip3 install flask
COPY webapp_flask.py /
```

ビルド

    docker build sample02/. -t local/flask:1.0
    docker images

### minikube上にデプロイ
デプロイ

    kubectl apply -f sample02/webapp-flask.yml
    kubectl get deployments
    curl $(minikube service webapp-flask --url)
