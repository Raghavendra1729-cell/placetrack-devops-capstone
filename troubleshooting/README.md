# Troubleshooting exercises

Two faults were introduced on purpose in the `placetrack` namespace of the local minikube cluster. Each one followed the same five steps: identify, investigate, root cause, fix, verify. The command output below is copied from real runs (see [`outputs/`](outputs/)).

## 1. Bad image tag (`broken-image.yaml`)

**Identify.** The Deployment exists but its Pod never becomes ready.

```
$ kubectl -n placetrack get pods -l app=tb-image
NAME                        READY   STATUS         RESTARTS   AGE
tb-image-7b4d867858-mmfpf   0/1     ErrImagePull   0          30s
```

**Investigate.** `kubectl describe pod` shows the pull failing and then backing off:

```
Warning  Failed   kubelet  Failed to pull image "ghcr.io/raghavendra1729-cell/placetrack-backend:does-not-exist": ... 403 Forbidden
Warning  Failed   kubelet  Error: ErrImagePull
Normal   BackOff  kubelet  Back-off pulling image "ghcr.io/raghavendra1729-cell/placetrack-backend:does-not-exist"
Warning  Failed   kubelet  Error: ImagePullBackOff
```

**Root cause.** The manifest points at a tag that does not exist in the registry (`does-not-exist`). GHCR answers with 403 for an unknown or private reference, so the kubelet cannot pull it. The container never starts, so it is a registry/manifest problem, not an application bug.

**Fix.** Point the Deployment at an image that exists:

```
kubectl -n placetrack set image deploy/tb-image app=ghcr.io/raghavendra1729-cell/placetrack-backend:local
```

**Verify.** The new Pod is `1/1 Running` and the old one terminates ([`outputs/02-image-fixed.txt`](outputs/02-image-fixed.txt)).

## 2. Service selector mismatch (`broken-service.yaml`)

**Identify.** The Pod is `Running` and the Service exists, yet nothing answers on the Service.

```
$ kubectl -n placetrack get endpoints tb-svc
NAME     ENDPOINTS   AGE
tb-svc   <none>      8s
```

**Investigate.** Compare what the Service selects with what the Pod is labelled:

```
$ kubectl -n placetrack get svc tb-svc -o jsonpath={.spec.selector}
{"app":"tb-service"}
$ kubectl -n placetrack get pod -l app=tb-svc --show-labels
tb-svc-746b6b6cc6-mwc4f   1/1   Running   0   18s   app=tb-svc,pod-template-hash=746b6b6cc6
```

**Root cause.** The Service selects `app=tb-service`, the Pod carries `app=tb-svc`. A Service only routes to Pods whose labels match its selector exactly, so it had no endpoints even though every Pod was healthy.

**Fix.**

```
kubectl -n placetrack patch svc tb-svc -p '{"spec":{"selector":{"app":"tb-svc"}}}'
```

**Verify.** The endpoint list now contains the Pod IP and a request through the Service returns `HTTP 200` ([`outputs/04-service-fixed.txt`](outputs/04-service-fixed.txt)).

## Takeaway

`Running` does not mean reachable. Check `READY`, then `describe` for events, then compare Service selectors with Pod labels via `get endpoints`.
