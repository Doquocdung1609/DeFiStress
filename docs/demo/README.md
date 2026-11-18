# DeFiStress Lab functional demo

The local preview integrates the accepted `c51d4d0` tree with exact candidate
files from PRs #57, #55, #58 and #53. It is a product demonstration, not a
scientific acceptance or a formal merge of those Draft PRs.

On Windows, from the repository root:

```powershell
.\scripts\start_demo.ps1
.venv\Scripts\python.exe scripts\demo_smoke.py
.\scripts\stop_demo.ps1
```

On Linux/macOS, with Python 3.12, pnpm, Node 24 and curl installed:

```bash
bash scripts/start_demo.sh
.venv/bin/python scripts/demo_smoke.py
bash scripts/stop_demo.sh
```

The local startup uses fixture mode, SQLite, ports 8100 and 3100, and no paid
source. The SQLite file and logs live under `data/runs/` and are ignored by Git.
The scripts refuse occupied ports or an existing process record. The frontend
opens at <http://localhost:3100/terra/overview> and API docs at
<http://localhost:8100/docs>.

Optional Docker Compose: `docker compose up --build` after Docker Desktop or
Engine is running. This mode uses PostgreSQL, Redis and a Celery worker; it was
configuration-validated but not runtime-tested in the Nov 18 Windows session
because the Docker daemon was unavailable.

See [Vietnamese runbook](DEFISTRESS_V2_DEMO_RUNBOOK_VI.md) and
[completion report](DEFISTRESS_V2_END_TO_END_COMPLETION.md).
