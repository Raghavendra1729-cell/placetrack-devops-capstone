# PlaceTrack

DevOps final project by Raghavendra (24BCS10250)

PlaceTrack is a small web app to keep track of job and internship applications. You add a company and a role, and move it through applied, interview, offer or rejected. The app is simple. The main work in this project is the DevOps part around it: tests, Docker, a CI pipeline with a security scan, Terraform, Kubernetes with Helm, and monitoring.

```mermaid
flowchart LR
    Code --> CI[GitHub Actions: pytest, build, Trivy]
    CI --> R[(GHCR image with SHA tag)]
    TF[Terraform] --> AWS[AWS VPC + EKS]
    R --> H[Helm]
    H --> K[Kubernetes]
    K --> M[Prometheus + Grafana]
```

| Part | Tools |
|---|---|
| Frontend | React, Vite, nginx |
| Backend | FastAPI, SQLAlchemy, Alembic |
| Database | PostgreSQL |
| CI/CD | GitHub Actions, GHCR, Trivy |
| Infrastructure | Terraform, AWS (VPC, EKS) |
| Deployment | Docker Compose, Kubernetes, Helm |
| Monitoring | Prometheus, Grafana |

```text
backend/            FastAPI app, migration, tests, Dockerfile
frontend/           React app, Dockerfile
docker-compose.yml  postgres, backend and frontend
helm/placetrack/    Helm chart
k8s/                namespace
terraform/          VPC and EKS
monitoring/         Prometheus and Grafana setup
troubleshooting/    two broken manifests and how I fixed them
scripts/            deploy and load test scripts
.github/workflows/  CI/CD pipeline
docs/               presentation
images/             screenshots
```

## M1 Application

The backend has these endpoints: `GET/POST /api/jobs`, `GET/PUT/DELETE /api/jobs/{id}`, `GET /api/jobs/stats`, `/health`, `/ready` and `/metrics`. The `jobs` table is created by the Alembic migration in `backend/alembic/versions/`. The API docs are at `/docs`.

![App](images/01-app-compose.png)

![App on a phone](images/01b-app-mobile.png)

## M2 Tests

There are 16 pytest tests. They cover all the endpoints, validation errors, 404s, `/metrics`, and `/ready` returning 503 when the database is down. The tests use an in-memory SQLite database instead of Postgres. The config is in `backend/pytest.ini`.

```bash
cd backend
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
pytest -v
```

![pytest](images/02-pytest.png)

## M3 Git

I made small commits with clear messages. `.gitignore` covers `.env`, `__pycache__`, `node_modules`, `.venv` and Terraform state. Gitleaks found no secrets in the history.

![git log](images/04-git-log.png)

## M4 Docker

The backend image runs as user 10001. The frontend Dockerfile is multi-stage (Node builds the app, nginx serves it) and runs as user 101. Docker Compose starts postgres, the backend and the frontend.

```bash
docker compose up --build      # open http://localhost:3000
```

![docker compose](images/03-compose-up.png)

## M5 CI/CD

The workflow `.github/workflows/ci-cd.yml` runs on every push to `main`. It runs pytest, builds the frontend, builds both Docker images, scans them with Trivy and pushes them to GHCR as `ghcr.io/raghavendra1729-cell/placetrack-<service>:<commit SHA>`. If a test fails or Trivy finds a HIGH or CRITICAL problem, the pipeline stops and nothing is pushed. The images are tagged with the commit SHA and not `latest`.

After the images are pushed, the `deploy` job runs on a self-hosted runner on my laptop and deploys the new SHA to minikube with Helm. It only runs on `main` when the repository variable `DEPLOY_ENABLED` is `true`, so the pipeline still passes when the runner is off.

The first run on GitHub passed all four jobs: [Actions run](https://github.com/Raghavendra1729-cell/placetrack-devops-capstone/actions/runs/38557147918).

![Actions run](images/23-actions-run.png)

Both images are public in GHCR with the commit SHA as the tag:

![GHCR backend](images/24-ghcr-backend.png)

![GHCR frontend](images/25-ghcr-frontend.png)

## M6 Trivy

Trivy scans the backend and frontend images in the pipeline and fails on fixable HIGH or CRITICAL findings.

My first scan failed. The backend had 3 HIGH findings in Starlette 0.41.3 (for example CVE-2025-62727, a denial of service with crafted `Range` headers). The old Alpine nginx image in the frontend had 42 HIGH and CRITICAL findings in OpenSSL, libexpat and libxml2. I upgraded FastAPI, which brings Starlette 1.7.0, and moved to `nginx-unprivileged:1.30.5-alpine`. After that both images scanned clean. A clean result means there is no fixable HIGH or CRITICAL vulnerability in the image when it is scanned, so the scan runs on every build.

![Trivy before and after](images/05-trivy-before.png)

![Trivy clean](images/07-trivy-clean.png)

This is the same scan in the pipeline. GitHub only shows job logs to signed-in users, so the image is the text of the Trivy step taken with `gh run view --log`. Both images show 0 vulnerabilities.

![Trivy in the pipeline](images/26-trivy-pipeline.png)

## M7 Terraform

`terraform/` creates a VPC with two public subnets in two availability zones and an EKS cluster with a managed node group of two `t3.small` nodes. The API endpoint is limited to my IP with the `api_access_cidrs` variable, which I set in a `terraform.tfvars` file that is not committed. No credentials are stored in the repo.

```bash
cd terraform
terraform init
terraform validate
terraform plan -out=tfplan
terraform apply tfplan
terraform destroy
```

Plan:

![terraform plan](images/08-tf-plan.png)

Apply:

![terraform apply](images/09-tf-apply.png)

Both nodes are Ready and the system pods are running:

![EKS nodes](images/12b-eks-nodes.png)

AWS Console, the VPC with its two public subnets and the EKS cluster:

![AWS VPC](images/11-aws-vpc.png)

![AWS EKS](images/12-aws-eks.png)

After the screenshots I ran `terraform destroy`:

![terraform destroy](images/10-tf-destroy.png)

## M8 Kubernetes and Helm

The Helm chart in `helm/placetrack` creates the backend and frontend (2 replicas each), ClusterIP services, an Ingress for the host `placetrack.local` (`/` goes to the frontend and `/api` to the backend), Postgres, a Job for the migration and an HPA, all in the `placetrack` namespace.

```bash
minikube start -p placetrack --driver=docker --cpus=4 --memory=5500
minikube -p placetrack addons enable ingress
minikube -p placetrack addons enable metrics-server
docker build -t ghcr.io/raghavendra1729-cell/placetrack-backend:local backend
docker build -t ghcr.io/raghavendra1729-cell/placetrack-frontend:local frontend
minikube -p placetrack image load ghcr.io/raghavendra1729-cell/placetrack-backend:local ghcr.io/raghavendra1729-cell/placetrack-frontend:local
kubectl apply -f k8s/namespace.yaml
helm upgrade --install placetrack helm/placetrack -n placetrack --wait
kubectl -n ingress-nginx port-forward svc/ingress-nginx-controller 8080:80      # open http://placetrack.local:8080
```

The host name needs this line in `/etc/hosts`: `127.0.0.1 placetrack.local`.

![pods](images/13-kubectl-pods.png)

![services, ingress, hpa](images/14-kubectl-svc.png)

![helm list](images/15-helm-list.png)

![app through the ingress](images/16-app-ingress.png)

## M9 Monitoring

The backend exposes `/metrics`. `monitoring/install.sh` installs Prometheus and Grafana, and the ServiceMonitor in the chart makes Prometheus scrape the backend.

```bash
./monitoring/install.sh
helm upgrade placetrack helm/placetrack -n placetrack --reuse-values --set serviceMonitor.enabled=true
./scripts/load-test.sh http://localhost:8080 60
```

![metrics](images/17-metrics.png)

![prometheus targets](images/18-prom-targets.png)

![grafana](images/19-grafana.png)

## Troubleshooting

I broke two things on purpose and fixed them: a wrong image tag (`ImagePullBackOff`) and a Service selector typo (no endpoints). The steps and the output are in [troubleshooting/](troubleshooting/README.md).

![ImagePullBackOff](images/20-ts-image-error.png)

![selector mismatch](images/21-ts-selector.png)

![selector fixed](images/22-ts-selector-fixed.png)

## Live demo

Before the demo, minikube and the runner are started and the repository variable `DEPLOY_ENABLED` is `true`.

1. Show the running app at `http://placetrack.local:8080`.
2. Change the subtitle in `frontend/src/App.jsx`, then `git commit` and `git push`.
3. Show the pipeline run in GitHub Actions: test, frontend, image and then deploy.
4. The deploy job runs `scripts/deploy.sh` with the commit SHA on my laptop. Show the pods being replaced with `kubectl -n placetrack get pods -w`.
5. Refresh the browser to see the change.

## What I learned

* A build that passes can still have security problems. Trivy failed my first images.
* nginx looks up the backend name only once at startup, and its resolver does not use the DNS search domains. Using the full name `<service>.<namespace>.svc.cluster.local` fixed the 502 error.
* A running pod is not always ready, and a ready pod is not always reachable.
* The database password Secret has to stay after `helm uninstall`, because the volume keeps the old password.
* Passwords and keys are generated when deploying and are never committed.
