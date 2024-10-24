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
```bash
$ export KUBE_MLFLOW_TRACKING_URI=http://mlflow-tracking
$ export MLFLOW_TRACKING_URI=http://localhost:8080
$ export MLFLOW_TRACKING_USERNAME=user
$ export MLFLOW_TRACKING_PASSWORD=Xtm1GRAAbr
```
```bash
$ mlflow run https://github.com/326-T/mlflow-project-sample.git \
  --experiment-name wine_quality \
  --backend kubernetes \
  --backend-config .kube/kubernetes_config.json \
  -P alpha=0.5
```