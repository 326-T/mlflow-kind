# Ingress Nginx での動作検証

## 動作確認

2 つの ConfigMap を編集する必要がある

```
$ k edit configmaps -n kserve inferenceservice-config
```

- data.ingress.disableIstioVirtualHost: true
- data.ingress.disableIngressCreation: true

```yaml
data:
  ingress: |-
    {
        "ingressGateway" : "knative-serving/knative-ingress-gateway",
        "knativeLocalGatewayService" : "",
        "localGateway" : "knative-serving/knative-local-gateway",
        "localGatewayService" : "ingress-nginx-controller.ingress-nginx.svc.cluster.local",
        "ingressClassName" : "nginx",
        "ingressDomain"  : "example.com",
        "additionalIngressDomains": [
        ],
        "domainTemplate": "{{ .Name }}-{{ .Namespace }}.{{ .IngressDomain }}",
        "urlScheme": "http",
        "disableIstioVirtualHost": true,
        "disableIngressCreation": true
    }
```

```
$ k edit configmaps -n knative-serving config-network
```

```yaml
data:
  ingress-class: nginx
```
