from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any

import duckdb
from pydantic import BaseModel, Field


LABEL = 'Eval Coverage Compiler'
FIXTURE = 'eval_coverage_cases.jsonl'
ANALYSIS = 'eval_coverage_analysis.json'
CSV_NAME = 'missing_simulations.csv'
DASHBOARD_TITLE = 'Eval Coverage Gaps'
PRIMARY_METRIC = 'coverage_score'
PRIMARY_LABEL = 'Coverage'
CHECKS = ['untested refund escalation path', 'missing persona diversity', 'release diff creates new eval', 'unsupported scenario blocked']
CASES = [['refund escalation', 'add_missing_simulation', 'persona=angry_customer; tool=refund_tool; metric=escalation_metric', False, 94, 'release_diff', 'missing high-risk refund escalation simulation'], ['billing correction', 'covered_review', 'persona=non_native_speaker; tool=billing_tool; metric=resolution_metric', True, 35, 'docs', 'covered but needs persona expansion'], ['account closure', 'add_missing_simulation', 'persona=elderly_user; tool=identity_tool; metric=safety_metric', False, 88, 'production_trace', 'identity flow lacks edge-case simulation'], ['order status', 'covered_review', 'persona=standard_user; tool=order_tool; metric=latency_metric', True, 18, 'eval_suite', 'adequately covered baseline path'], ['policy exception', 'add_missing_simulation', 'persona=agent_handoff; tool=policy_tool; metric=compliance_metric', False, 91, 'release_diff', 'new policy tool has no regression eval']]
SLUG = 'eval-coverage-compiler'


class DomainCase(BaseModel):
    case_id: str
    subject: str
    recommendation: str
    reason: str
    evidence_backed: bool
    score: int = Field(ge=0, le=100)
    evidence_id: str
    evidence: str
    notes: str


def should_enable(config: dict[str, Any]) -> bool:
    return config.get("slug") == SLUG


def generate_domain_fixtures(fixtures: Path) -> dict[str, Any]:
    cases = [
        DomainCase(
            case_id=f"domain_case_{index:03d}",
            subject=row[0],
            recommendation=row[1],
            reason=row[2],
            evidence_backed=row[3],
            score=row[4],
            evidence_id=f"domain_ev_{index:04d}",
            evidence=row[5],
            notes=row[6],
        )
        for index, row in enumerate(CASES, start=1)
    ]
    with (fixtures / FIXTURE).open("w", encoding="utf-8") as handle:
        for case in cases:
            handle.write(case.model_dump_json() + "\n")
    return {"domain_cases": len(cases)}


def load_domain_cases(fixtures: Path) -> list[DomainCase]:
    path = fixtures / FIXTURE
    if not path.exists():
        return []
    return [DomainCase.model_validate_json(line) for line in path.read_text(encoding="utf-8").splitlines()]


def ingest_domain_cases(db_path: Path, cases: list[DomainCase]) -> int:
    if not cases:
        return 0
    with duckdb.connect(str(db_path)) as conn:
        conn.execute(
            """
            create table if not exists domain_cases (
                case_id varchar primary key,
                subject varchar,
                recommendation varchar,
                reason varchar,
                evidence_backed boolean,
                score integer,
                evidence_id varchar,
                evidence varchar,
                notes varchar
            )
            """
        )
        for case in cases:
            conn.execute(
                "insert into domain_cases values (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                [
                    case.case_id,
                    case.subject,
                    case.recommendation,
                    case.reason,
                    case.evidence_backed,
                    case.score,
                    case.evidence_id,
                    case.evidence,
                    case.notes,
                ],
            )
    return len(cases)


def domain_cases_from_db(root: Path) -> list[DomainCase]:
    db_path = root / "data" / "app.duckdb"
    with duckdb.connect(str(db_path), read_only=True) as conn:
        exists = conn.execute(
            "select count(*) from information_schema.tables where table_name = 'domain_cases'"
        ).fetchone()[0]
        if not exists:
            return []
        rows = conn.execute("select * from domain_cases order by case_id").fetchall()
    return [
        DomainCase(
            case_id=row[0],
            subject=row[1],
            recommendation=row[2],
            reason=row[3],
            evidence_backed=row[4],
            score=row[5],
            evidence_id=row[6],
            evidence=row[7],
            notes=row[8],
        )
        for row in rows
    ]


def analyze_domain(root: Path) -> dict[str, Any]:
    cases = domain_cases_from_db(root)
    if not cases:
        return {}
    missing_or_blocked = [
        case for case in cases if not case.evidence_backed or case.recommendation in {"reject", "block_claim", "no_go", "quarantine"}
    ]
    by_recommendation = Counter(case.recommendation for case in cases)
    average_score = round(sum(case.score for case in cases) / len(cases), 2)
    ranked = sorted(cases, key=lambda case: (not case.evidence_backed, 100 - case.score, case.case_id))
    result = {
        "label": LABEL,
        "dashboard_title": DASHBOARD_TITLE,
        "primary_metric": PRIMARY_METRIC,
        "primary_label": PRIMARY_LABEL,
        "cases": [case.model_dump() for case in ranked],
        "case_count": len(cases),
        "average_score": average_score,
        "missing_or_blocked_count": len(missing_or_blocked),
        "recommendation_counts": dict(sorted(by_recommendation.items())),
        "checks": CHECKS,
        "top_risk": min(cases, key=lambda case: (case.evidence_backed, case.score)).model_dump(),
    }
    outputs = root / "outputs"
    (outputs / ANALYSIS).write_text(json.dumps(result, indent=2), encoding="utf-8")
    with (outputs / CSV_NAME).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "case_id",
                "subject",
                "recommendation",
                "reason",
                "evidence_backed",
                "score",
                "evidence_id",
                "evidence",
                "notes",
            ],
        )
        writer.writeheader()
        for case in ranked:
            writer.writerow(case.model_dump())
    return result


def evidence_ids_from_db(root: Path) -> set[str]:
    return {case.evidence_id for case in domain_cases_from_db(root)}
