# Eval Coverage Compiler

A local evaluation coverage workbench that turns synthetic agent-test records into coverage gaps, risk-ranked recommendations, and verifiable reports.

## Features

- Typed fixtures for scenarios, tools, personas, risk tiers, and outcomes.
- Coverage analysis across journey, persona, tool, and edge-case dimensions.
- Offline dashboard and evidence graph for audit-friendly evaluation planning.

## Run Locally

```bash
uv sync
uv run app init-demo
uv run app ingest fixtures/
uv run app analyze
uv run app verify
uv run app dashboard
uv run app benchmark
uv run app export-demo-pack
uv run pytest -q
uv run ruff check .
```

## Outputs

- `outputs/dashboard.html`
- `outputs/decision_report.md`
- `outputs/evidence_graph.mmd`
- `outputs/risk_or_quality_report.csv`
- `outputs/benchmark.md`
- `outputs/demo_pack.md`

## Data Policy

This project runs fully locally on deterministic synthetic fixtures. It does not require external APIs, credentials, private datasets, network access, or production systems.
