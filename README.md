# WebApp dev on PC

## 概要
- ごく簡単なWebアプリケーションを作成してみる
- Windows + Minikube環境上に構築
- ちょっとした開発や確認に。

## 構成
| 項目           | NIC    |
|:---------------|:-------|
| Windows        | 10     |
| VirtualBox     | 6.0.4  |
| Vagrant        | 2.2.4  |
| Minikube       | 0.34.1 |
| Kubernetes-cli | 1.13.4 |


## 環境準備
### 必要なソフトウェアのインストール
[chocolatey](https://chocolatey.org/)を使用します。

    choco install virtualbox
    choco install vagrant
    choco install minikube
    choco install kubernetes-cli

### Minikube環境の起動
minikubeを起動する。

    minikube start

起動を確認する。

    kubectl cluster-info
    kubectl get node
    minikube dashboard

### サービス起動

webappを起動

    kubectl apply -f webapp-deployment.yml

接続確認

    minikube service webapp

