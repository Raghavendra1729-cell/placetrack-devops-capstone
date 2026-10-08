# Trivy scan explanation (M6)

**What Trivy scanned.** The pipeline builds the backend and frontend Docker images and runs Trivy on each one before anything is pushed. Trivy looks inside the finished image at the operating-system packages and the Python and npm libraries, compares them with a vulnerability database, and the job is configured to fail (`exit-code: 1`) on fixable HIGH or CRITICAL findings.

**What it found.** The first scan failed. The backend had 3 HIGH findings in Starlette 0.41.3 (a dependency of the FastAPI version I had pinned), for example CVE-2025-62727, where crafted `Range` headers can cause a denial of service. The frontend, built on an older Alpine nginx image, had 42 HIGH and CRITICAL findings in system libraries such as OpenSSL (`libssl3`, CVE-2026-31789, a heap buffer overflow on 32-bit systems), libexpat and libxml2.

**What I did.** I upgraded FastAPI (which brings Starlette 1.7.0) and the other Python pins, and moved the frontend to `nginx-unprivileged:1.30.5-alpine`. I rebuilt both images and scanned again: both exit with code 0.

**What a clean result means.** No fixable HIGH or CRITICAL vulnerability is present in the image at scan time. It is a snapshot, not a guarantee, which is why the scan runs on every build.

Evidence: `images/05-trivy-before.png` (before and after exit codes) and `images/07-trivy-clean.png`.
