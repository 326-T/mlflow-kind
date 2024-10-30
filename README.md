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
$ kubectl port-forward svc/mlflow-tracking 8080:80 -n mlflow
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
$ export KUBE_MLFLOW_TRACKING_URI=http://mlflow-tracking.mlflow.svc.cluster.local
$ export MLFLOW_TRACKING_URI=http://localhost:8080
$ export MLFLOW_TRACKING_USERNAME=user
$ export MLFLOW_TRACKING_PASSWORD=cGFzc3dvcmQK=
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

```bash
$ cd kserve
$ kubectl apply -f inference_service.yaml
```

```bash
$ kubectl port-forward -n istio-system svc/knative-local-gateway 8081:80
```

[./kserve/predict.http](./kserve/predict.http)で推論を行う.

## CRDs

- cert-manager
  - challenges.acme.cert-manager.io
  - orders.acme.cert-manager.io
  - certificaterequests.cert-manager.io
  - certificates.cert-manager.io
  - clusterissuers.cert-manager.io
  - issuers.cert-manager.io
- istio
  - wasmplugins.extensions.istio.io
  - destinationrules.networking.istio.io
  - envoyfilters.networking.istio.io
  - gateways.networking.istio.io
  - proxyconfigs.networking.istio.io
  - serviceentries.networking.istio.io
  - sidecars.networking.istio.io
  - virtualservices.networking.istio.io
  - workloadentries.networking.istio.io
  - workloadgroups.networking.istio.io
  - authorizationpolicies.security.istio.io
  - peerauthentications.security.istio.io
  - requestauthentications.security.istio.io
  - telemetries.telemetry.istio.io
- knative
  - metrics.autoscaling.internal.knative.dev
  - podautoscalers.autoscaling.internal.knative.dev
  - images.caching.internal.knative.dev
  - certificates.networking.internal.knative.dev
  - clusterdomainclaims.networking.internal.knative.dev
  - ingresses.networking.internal.knative.dev
  - serverlessservices.networking.internal.knative.dev
  - configurations.serving.knative.dev
  - domainmappings.serving.knative.dev
  - revisions.serving.knative.dev
  - routes.serving.knative.dev
  - services.serving.knative.dev
- kserve
  - clusterservingruntimes.serving.kserve.io
  - clusterstoragecontainers.serving.kserve.io
  - inferencegraphs.serving.kserve.io
  - inferenceservices.serving.kserve.io
  - predictors.serving.kserve.io
  - servingruntimes.serving.kserve.io
  - trainedmodels.serving.kserve.io
- metallb
  - bfdprofiles.metallb.io
  - bgpadvertisements.metallb.io
  - bgppeers.metallb.io
  - communities.metallb.io
  - ipaddresspools.metallb.io
  - l2advertisements.metallb.io
  - servicel2statuses.metallb.io
