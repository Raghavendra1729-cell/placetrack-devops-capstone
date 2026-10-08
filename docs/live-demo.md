# Live demo (about 3 minutes)

Goal: commit a change, watch the pipeline run, see the deployment update.

Prerequisites (before recording): repository pushed to GitHub, GHCR packages set to Public, minikube running with the release installed (`scripts/deploy.sh <sha>`), `kubectl -n ingress-nginx port-forward svc/ingress-nginx-controller 8080:80` running.

1. **Show the running app** at `http://localhost:8080`.
2. **Change something visible.** In `frontend/src/App.jsx` change the subtitle `Track every job application in one place` to `Placement season edition`.
3. **Commit and push.**
   ```bash
   git add -A && git commit -m "Change dashboard subtitle for the demo" && git push
   ```
4. **Show the pipeline** in GitHub > Actions: pytest, frontend build, image build, Trivy, push. Point out the SHA tag on the pushed image.
5. **Deploy the new image.**
   ```bash
   scripts/deploy.sh "$(git rev-parse HEAD)"
   kubectl -n placetrack rollout status deploy/placetrack-frontend
   ```
6. **Refresh the browser** and show the new subtitle.

If the push is not possible on camera, use a fresh image tag so Helm actually rolls the pods (reusing the tag `local` changes nothing and nothing restarts):

```bash
TAG=demo-$(date +%H%M%S)
docker build -t ghcr.io/raghavendra1729-cell/placetrack-frontend:$TAG frontend
minikube -p placetrack image load ghcr.io/raghavendra1729-cell/placetrack-frontend:$TAG
helm upgrade placetrack helm/placetrack -n placetrack --reuse-values --set image.tag=$TAG --wait
```

The backend image must also exist under that tag, so also tag it (`docker tag ...placetrack-backend:local ...placetrack-backend:$TAG` then `minikube image load`). Explain that in the real flow CI builds and pushes the SHA-tagged images.
