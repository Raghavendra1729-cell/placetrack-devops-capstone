# Live demo (about 3 minutes)

Commit a change, watch the pipeline run, see the deployment update.

Before recording: the repository is pushed to GitHub, both GHCR packages are public, minikube is running with the release installed, and the Ingress port-forward is up:

```bash
kubectl -n ingress-nginx port-forward svc/ingress-nginx-controller 8080:80
```

1. Open `http://localhost:8080` and show the running app.
2. In `frontend/src/App.jsx` change the subtitle `Track every job application in one place` to `Placement season edition`.
3. Commit and push:
   ```bash
   git add -A && git commit -m "Change dashboard subtitle for the demo" && git push
   ```
4. In GitHub open Actions and show the run: pytest, frontend build, image build, Trivy, push. Point out that the image tag is the commit SHA.
5. Deploy that image:
   ```bash
   scripts/deploy.sh "$(git rev-parse HEAD)"
   kubectl -n placetrack rollout status deploy/placetrack-frontend
   ```
6. Refresh the browser and show the new subtitle.

If pushing on camera is not possible, build and load both images under a new tag, because reusing the tag `local` does not restart the pods:

```bash
TAG=demo-$(date +%H%M%S)
for s in backend frontend; do
  docker build -t ghcr.io/raghavendra1729-cell/placetrack-$s:$TAG $s
  minikube -p placetrack image load ghcr.io/raghavendra1729-cell/placetrack-$s:$TAG
done
scripts/deploy.sh $TAG
```

Say that in the real flow CI builds and pushes these images.
