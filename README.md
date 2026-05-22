# Hub24 STO Training - Demo Applicationdemo

A deliberately vulnerable Python Flask application for Harness STO hands-on training.

**WARNING: This application contains intentional security vulnerabilities. Do NOT deploy to production.**

## What's Included

| Scan Type | File(s) | What To Find |
|-----------|---------|--------------|
| Secrets Detection | `src/app.py`, `src/config.py` | Hardcoded API keys, passwords, tokens |
| SCA | `requirements.txt` | Vulnerable Python dependencies |
| SAST | `src/app.py` | SQL injection, XSS, insecure patterns |
| Code Quality | `src/app.py` | Code smells, unused variables, complexity |
| DAST | Running app on port 5000 | Runtime injection, misconfig |
| IaC | `terraform/`, `k8s/` | Misconfigurations, no encryption, open access |
| Container | `Dockerfile` | Vulnerable base image, root user, secrets in layers |

## Run Locally

```bash
pip install -r requirements.txt
cd src && python app.py
```

App runs at http://localhost:5000
