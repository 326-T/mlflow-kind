# Install MLflow via kustomize

## Update manifests

### cert-manager
- [公式のドキュメント](https://cert-manager.io/docs/installation/kubectl/)参照
- [https://github.com/cert-manager/cert-manager/releases/download/v1.16.2/cert-manager.yaml](https://github.com/cert-manager/cert-manager/releases/download/v1.16.2/cert-manager.yaml)からダウンロード

### metallb
- [公式のドキュメント](https://metallb.io/installation/)参照
- refのバージョンを更新する

### metrics-server
- [GitHub](https://github.com/kubernetes-sigs/metrics-server/tree/master/manifests/base)
- refのバージョンを更新する

### knative-serving
- [公式のドキュメント](https://knative.dev/docs/install/yaml-install/serving/install-serving-with-yaml/#verifying-image-signatures)参照
- 以下の2つをインストール
  - [knative core](https://github.com/knative/serving/releases/download/knative-v1.16.0/serving-core.yaml)
  - [istio gateway](https://github.com/knative/net-istio/releases/download/knative-v1.16.0/istio.yaml)

他にもいくつかの設定があるのでドキュメントを確認する

### kserve
[公式のドキュメント](https://kserve.github.io/website/master/admin/serverless/serverless/#4-install-kserve)参照

ただしCRDファイルは大きすぎるので`minimal`を使う [#3487](https://github.com/kserve/kserve/issues/3487)

helm chartからマニフェストを生成
```bash
$ helm template kserve-crd oci://ghcr.io/kserve/charts/kserve-crd-minimal --version v0.14.0 > kserve-crd-minimal.yaml
$ helm template kserve oci://ghcr.io/kserve/charts/kserve --version v0.14.0 > kserve.yaml
```

- [kserve-crd-minimal](https://github.com/kserve/kserve/tree/master/charts/kserve-crd-minimal)
- [kserve-resource](https://github.com/kserve/kserve/tree/master/charts/kserve-resources)

### MLflow
1. bitnamiのhelm chartを使う
    ```bash
    $ helm template mlflow oci://registry-1.docker.io/bitnamicharts/mlflow \
      --namespace mlflow \
      --version 2.0.3 \
      --set tracking.auth.password=password \
      --set 'tracking.extraEnvVars[0].name=MLFLOW_HTTP_REQUEST_TIMEOUT' \
      --set 'tracking.extraEnvVars[0].value="600"' \
      --set 'tracking.extraArgs[0]=--gunicorn-opts=--timeout\ 600' \
      --set tracking.resources.requests.ephemeral-storage=2Gi \
      --set tracking.resources.limits.ephemeral-storage=10Gi \
      --set minio.auth.rootPassword=password \
      --set postgresql.auth.password=password > mlflow.yaml
    ```
2. 関係のないリソースを削除<br/>
   bitnamiのchartはminioとpostgresqlも一緒にインストールするので、関係のないリソースを削除する