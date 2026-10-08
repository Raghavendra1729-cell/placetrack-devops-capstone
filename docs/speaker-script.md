# Speaker script

About 30 to 45 seconds per slide (about 8 minutes), then the live demo.

## Slide 1: Title

Hello, I am Raghavendra. This is my DevOps capstone: PlaceTrack, a job application tracker. The app is small on purpose; the project is about everything around it - testing, containers, CI/CD, security scanning, Terraform, Kubernetes with Helm, and monitoring.

## Slide 2: What I built

PlaceTrack lets me track every job application. The interesting part is the path: code goes through GitHub Actions for tests, builds and a security scan, images go to a registry tagged with the commit, Terraform builds the AWS network and cluster, Helm deploys, and Prometheus and Grafana watch it. Each module of the course maps to one piece of this chain, and every screenshot in this deck is a real capture.

## Slide 3: M1 Application

The backend is FastAPI with SQLAlchemy and an Alembic migration that creates the jobs table in PostgreSQL. It has full create, read, update, delete endpoints plus a stats endpoint, and health, ready and metrics endpoints for Kubernetes and Prometheus. The React dashboard shows counts, filters and an add and edit form, and it reflows to phone width, as you can see on the right.

## Slide 4: M2 Tests

There are sixteen pytest tests. They never touch the real database: FastAPI's dependency override swaps in an in-memory SQLite database. They cover every endpoint, the 404 and validation errors, the metrics endpoint, and the readiness check returning 503 when the database is unavailable. This is the real pytest output from my machine.

## Slide 5: M3 Git

Version control is small, descriptive commits. The gitignore keeps environment files, caches, node modules, virtual environments and Terraform state out of the repository, and Gitleaks confirms there are no secrets anywhere in the history.

## Slide 6: M4 Docker

The backend and frontend images both run as non-root users. The frontend Dockerfile is multi-stage: Node builds the bundle, and an unprivileged nginx image serves it. One command, docker compose up with build, starts Postgres, the backend with its migrations, and the frontend. The screenshot shows all three services up and the user IDs inside the containers.

## Slide 7: M5 CI/CD

The workflow runs on every push to main. It runs pytest, builds the frontend, builds both Docker images, scans them with Trivy, and only then pushes them to GitHub Container Registry, tagged with the commit SHA instead of latest. If a test fails or Trivy finds a fixable high or critical vulnerability, nothing is published. I hardened the workflow so third-party actions are pinned to exact commits and only the image job can write packages. I have not pushed the repository yet, so I ran each of these steps locally; the live run link comes after the first push.

## Slide 8: M6 Trivy

Trivy scans both images for fixable high and critical vulnerabilities and fails the pipeline if it finds any. My first scan really failed: the backend had three high findings in Starlette, for example CVE-2025-62727, where crafted Range headers can cause denial of service, and the old nginx base image had forty-two high and critical findings in system libraries such as OpenSSL. I fixed them by upgrading FastAPI, which brings a patched Starlette, and moving to a current nginx image. Both scans now exit with zero. A clean scan means no fixable high or critical vulnerability exists in the image at scan time, which is why it runs on every build.

## Slide 9: M7 Terraform

Terraform builds a VPC with two public subnets in two availability zones and an EKS cluster with a managed node group of two nodes. I restricted the cluster API to my own IP address, and gave the EBS storage driver its own narrowly scoped role instead of attaching a policy to every node. The plan shows fifty-three resources to add and nothing to change or destroy. Applying creates billable resources, so the apply, the console screenshots and the destroy are the remaining evidence for this module.

## Slide 10: M8 Kubernetes

A single Helm chart deploys everything into the placetrack namespace: two replicas each of the backend and frontend, a Postgres StatefulSet, ClusterIP services, an Ingress that sends slash to the frontend and slash api to the backend, and a horizontal pod autoscaler. A Helm hook job runs the database migration after install. All pods are running with zero restarts.

## Slide 11: M8 Ingress

This is the application loaded in a browser through the Kubernetes Ingress controller. The page comes from the frontend service, and its calls to slash api are routed by the same Ingress to the backend, which talks to Postgres. The chart is the same for minikube and for EKS.

## Slide 12: M9 Observability

The backend exposes Prometheus metrics. A ServiceMonitor tells Prometheus to scrape both backend pods, and the targets page shows both up. The Grafana dashboard I built shows request rate per endpoint, the ninety-fifth percentile latency, error responses and the number of healthy backend pods. These panels have live data from a load test, not mock data.

## Slide 13: Troubleshooting

I broke the cluster in two ways and fixed both. First, a deployment with an image tag that does not exist ends in ErrImagePull and ImagePullBackOff; describe pod showed the pull failure and the fix was a valid tag. Second, a service whose selector had a typo: the pod was Running but the service had no endpoints, so nothing was reachable. Comparing the selector with the pod labels revealed it. The full five-step write-ups are in the troubleshooting folder.

## Slide 14: Live demo

For the live demo I change a visible string in the React app, commit and push. GitHub Actions runs the tests, builds, scans and pushes the images tagged with the new commit. Then I run the deploy script with that SHA, Helm rolls out the new pods, and refreshing the browser shows the change.

## Slide 15: Lessons

Four things I will remember. A passing build is not a secure build: Trivy failed my first images and I had to fix real vulnerabilities. nginx resolves upstream names once at startup, which caused a crash loop until I used a runtime resolver, and a review then showed its resolver ignores search domains, so I switched to the full service DNS name and the 502 became a 200. Running does not mean ready, and ready does not mean reachable. And secrets are generated at deploy time, never committed. Thank you.
