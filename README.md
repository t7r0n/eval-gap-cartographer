# Eval Coverage Compiler

A local evaluation coverage workbench that turns synthetic agent-test records into coverage gaps, risk-ranked recommendations, and verifiable reports.

`coval-eval-coverage-compiler` favors explicit fixtures, deterministic checks, and reviewable artifacts over hidden services or live data.

## Failure model

Eval Coverage Compiler: Missing Scenario Detection for Agent Teams.

## Measurement loop

- Typed fixtures for scenarios, tools, personas, risk tiers, and outcomes.
- Coverage analysis across journey, persona, tool, and edge-case dimensions.
- Offline dashboard and evidence graph for audit-friendly evaluation planning.

## Commands

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

## Test path

```bash
uv run ruff check .
uv run pytest -q
uv run app verify
```

## Local-only contract

Every example in `coval-eval-coverage-compiler` is fabricated for repeatability. Generated outputs are rebuildable artifacts, not source material.
