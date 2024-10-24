### トラッキングサーバのデプロイ

```bash
$ kind create cluster --name mlflow-poc
```

```bash
$ cd mlflow-server
$ helmfile apply
```

### トラッキングサーバへのアクセス

ポートフォワード

```bash
$ kubectl port-forward svc/mlflow-tracking 5000:80 -n mlflow
```

トラッキングサーバのアカウント確認

```bash
$ kubectl get secret --namespace mlflow mlflow-tracking -o yaml
```

### 学習

mlflow クライアントのインストール

```bash
$ cd mlflow-cli
$ pyenv local 3.12.2
$ python -m venv .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt
```

接続情報の設定

```bash
$ export MLFLOW_TRACKING_URI=http://localhost:8080
$ export MLFLOW_TRACKING_USERNAME=user
$ export MLFLOW_TRACKING_PASSWORD=Xtm1GRAAbr
```

学習の実行

```bash
$ mlflow run https://github.com/326-T/mlflow-project-sample.git \
  --experiment-name wine_quality \
  --backend kubernetes \
  --backend-config .kube/kubernetes_config.json \
  -P alpha=0.5
```
