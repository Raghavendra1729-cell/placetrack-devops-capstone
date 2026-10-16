# Troubleshooting exercises

I broke two things on purpose in the `placetrack` namespace of the local minikube cluster and fixed them with the same five steps each time: identify, investigate, root cause, fix, verify. The output below is from the real runs, and the screenshots are in [`images/`](../images/).

## 1. Bad image tag (`broken-image.yaml`)

**Identify.** The Deployment exists but its Pod never becomes ready.

```
$ kubectl -n placetrack get pods -l app=tb-image
NAME                        READY   STATUS         RESTARTS   AGE
tb-image-7b4d867858-k2d74   0/1     ErrImagePull   0          40s
```

**Investigate.** `kubectl describe pod` shows the pull failing and then backing off:

```
Warning  Failed   kubelet  Failed to pull image "ghcr.io/raghavendra1729-cell/placetrack-backend:does-not-exist": ... not found
Warning  Failed   kubelet  Error: ErrImagePull
Normal   BackOff  kubelet  Back-off pulling image "ghcr.io/raghavendra1729-cell/placetrack-backend:does-not-exist"
Warning  Failed   kubelet  Error: ImagePullBackOff
```

**Root cause.** The manifest points at a tag that does not exist in GHCR (`does-not-exist`), so the kubelet cannot pull it. The container never starts, so it is a manifest problem, not an application bug.

**Fix.** Point the Deployment at a tag the pipeline really pushed (the commit SHA):

```
$ kubectl -n placetrack set image deploy/tb-image app=ghcr.io/raghavendra1729-cell/placetrack-backend:1ac201e89e13c9bae4d410cdfbc93283a0365b50
deployment.apps/tb-image image updated
deployment "tb-image" successfully rolled out
```

**Verify.** The new Pod is `1/1 Running` and the old one terminates:

```
$ kubectl -n placetrack get pods -l app=tb-image
NAME                        READY   STATUS        RESTARTS   AGE
tb-image-7b4d867858-k2d74   0/1     Terminating   0          79s
tb-image-96576c48b-9bklj    1/1     Running       0          0s
```

## 2. Service selector mismatch (`broken-service.yaml`)

**Identify.** The Pod is `Running` and the Service exists, yet the Service has no endpoints.

```
$ kubectl -n placetrack get endpoints tb-svc
NAME     ENDPOINTS   AGE
tb-svc   <none>      8s
```

**Investigate.** Compare what the Service selects with what the Pod is labelled:

```
$ kubectl -n placetrack get svc tb-svc -o jsonpath='{.spec.selector}'
{"app":"tb-service"}
$ kubectl -n placetrack get pods -l app=tb-svc --show-labels
tb-svc-746b6b6cc6-ng68j   1/1   Running   0   8s   app=tb-svc,pod-template-hash=746b6b6cc6
```

**Root cause.** The Service selects `app=tb-service`, the Pod carries `app=tb-svc`. A Service only routes to Pods whose labels match its selector exactly, so it had no endpoints even though the Pod was healthy.

**Fix.**

```
$ kubectl -n placetrack patch svc tb-svc -p '{"spec":{"selector":{"app":"tb-svc"}}}'
service/tb-svc patched
```

**Verify.** The endpoint list now has the Pod IP:

```
$ kubectl -n placetrack get endpoints tb-svc
NAME     ENDPOINTS        AGE
tb-svc   10.244.0.23:80   26s
```
