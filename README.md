## トラッキングサーバのデプロイ

```bash
$ kind create cluster --name mlflow-poc
```

```bash
$ cd mlflow-server
$ helmfile sync
```

## トラッキングサーバへのアクセス

ポートフォワード

```bash
$ kubectl port-forward svc/mlflow-tracking 8080:80 -n mlflow
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
$ export MLFLOW_TRACKING_PASSWORD=password
```

学習の実行

```bash
$ python scripts/cli.py \
  fine-tune \
  326takeda/mlflow-project_multilingual-e5-large:latest \
  430758536676277373 \
  sample-run
```

## KServe へのデプロイ

```bash
$ python scripts/cli.py \
  deploy \
  sample-inference-service \
  430758536676277373 \
  c3dce6c6bcc245c2b7dd37924bb958e0 \
  multilingual-e5-large
```

```bash
$ kubectl port-forward -n istio-system svc/knative-local-gateway 8081:80
```

[./predict.http](./predict.http)で推論を行う.

### REST v1

```
HTTP/1.1 200 OK
content-length: 86687
content-type: application/json
date: Mon, 11 Nov 2024 01:30:13 GMT
server: istio-envoy
x-envoy-upstream-service-time: 23032
connection: close

{
  "predictions": [
    [0.022029250860214233,...],
    [0.062769208473405843,...],
    [0.069207439856743254,...],
    [0.023856797154736583,...],
  ]
}
```

### REST v2

```
HTTP/1.1 200 OK
content-length: 86877
content-type: application/json
date: Mon, 11 Nov 2024 01:30:53 GMT
server: istio-envoy
x-envoy-upstream-service-time: 21119
connection: close

{
  "model_name": "multilingual-e5-large",
  "model_version": null,
  "id": "none",
  "parameters": null,
  "outputs": [
    {
      "name": "embeddings",
      "shape": [
        4,
        1024
      ],
      "datatype": "FP32",
      "parameters": null,
      "data": [0.0288118626922369,...]
    }
  ]
}
```

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
