# Trivy scan (M6)

Trivy runs in the pipeline on both the backend and the frontend image, after the build and before the push, and it fails the job on any fixable HIGH or CRITICAL vulnerability. It checks the operating system packages and the Python and npm libraries inside each image against a vulnerability database. My first scan failed: the backend had 3 HIGH findings in Starlette 0.41.3 (for example CVE-2025-62727, a denial of service through crafted `Range` headers), and the frontend's old Alpine base had 42 HIGH and CRITICAL findings in OpenSSL, libexpat and libxml2. I upgraded FastAPI, which brings Starlette 1.7.0, and moved to `nginx-unprivileged:1.30.5-alpine`, and both images now scan clean with exit code 0. A clean result means no fixable HIGH or CRITICAL vulnerability is in the image at scan time, so the scan has to run on every build.

Evidence: `images/05-trivy-before.png` and `images/07-trivy-clean.png`.
