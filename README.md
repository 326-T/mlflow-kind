## トラッキングサーバのデプロイ

```bash
$ kind create cluster --name mlflow-poc
```

```bash
$ cd mlflow-server
$ helmfile apply
```

## トラッキングサーバへのアクセス

ポートフォワード

```bash
$ kubectl port-forward svc/mlflow-tracking 5000:80 -n mlflow
```

トラッキングサーバのアカウント確認

```bash
$ kubectl get secret --namespace mlflow mlflow-tracking -o yaml
```

## 学習

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
$ export KUBE_MLFLOW_TRACKING_URI=http://tracking-server.mlflow.svc.cluster.local
$ export MLFLOW_TRACKING_URI=http://localhost:8080
$ export MLFLOW_TRACKING_USERNAME=user
$ export MLFLOW_TRACKING_PASSWORD=zJJwlMdMZb
```

学習の実行

```bash
$ mlflow run https://github.com/326-T/mlflow-project-sample.git \
  --experiment-name wine_quality \
  --backend kubernetes \
  --backend-config .kube/kubernetes_config.json \
  -P alpha=0.5
```

## KServe へのデプロイ

### パラメータの修正

[./kserve/inference_service.yaml](./kserve/inference_service.yaml)を修正する.

1. モデルのパスを修正
1. AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY を設定

AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY は以下で確認する.

```bash
$ kubectl get secret -n mlflow mlflow-minio -o yaml
```

```bash
$ cd kserve
$ kubectl apply -f inference_service.yaml
```

[./kserve/predict.http](./kserve/predict.http)で推論を行う.
