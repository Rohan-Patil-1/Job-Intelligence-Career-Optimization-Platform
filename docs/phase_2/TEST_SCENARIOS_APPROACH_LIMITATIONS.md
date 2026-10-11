# Phase 2 — Test Scenarios, Engineering Approach, and Limitations

## 1. Purpose and evidence standard

This document describes **distinct failure-oriented test scenarios** for the Job Intelligence & Career Optimization Platform's Phase 2: Market Analysis & Role Intelligence. It also explains our design approach, why each scenario matters, and where the system remains limited.

**Validation status:** The development environment reported **183 passing pytest tests** in the full regression suite. The scenario catalog below is an engineering test specification, **not a claim that every scenario has its own implemented automated test**. Each scenario is labeled either **Existing test area** (a related test module exists; verify the precise assertion in source) or **Proposed extension** (additional test to implement). Example values are illustrative unless identified as an observed pilot.

## 2. Our engineering approach

We use a staged, evidence-aware workflow:

1. **Preserve source data.** Normalize Adzuna job records and store them in the canonical `jobs` table. Preserve provenance and do not replace the original description merely because longer text is found elsewhere.
2. **Assess data quality before ranking.** Inspect missing descriptions, description length, inconsistent fields, and potential duplicates. Weak data should be visible to the analyst instead of silently treated as negative evidence.
3. **Extract interpretable signals.** Use skill vocabularies, domain keywords, role and seniority rules, and a candidate profile to derive explainable matches and gaps.
4. **Separate fit from evidence strength.** Opportunity scoring considers technical match, role fit, seniority fit, and domain evidence. A recommendation can have an apparent fit but still lack sufficient description evidence.
5. **Enrich conservatively.** Discover candidate job pages, resolve URLs, validate provenance, extract JSON-LD/HTML content, and store supplemental text in `job_enrichments` with source metadata and validation status.
6. **Compare without promoting.** Evaluate baseline versus enriched evidence using a transient job copy. Report provisional score changes separately; do not overwrite the canonical description or automatically promote unverified third-party evidence.
7. **Test in layers.** Use deterministic unit tests for extraction/scoring, repository tests for persistence, and end-to-end CLI or external-service checks for integration. Run the full regression suite before publishing changes.

### Design principles

- **Auditability:** retain the baseline record, source URL, validation status, and extraction method.
- **Conservatism:** missing information is not equivalent to a missing skill; third-party claims are not employer verification.
- **Explainability:** expose matched/missing skills, evidence score, recommendation, and confidence rather than a single unexplained rank.
- **Non-destructive evaluation:** compare candidate evidence in memory before deciding whether it merits further review.
- **Repeatability:** make scoring deterministic for a fixed profile, job record, and vocabulary.

## 3. Unique test scenarios

### A. Ingestion and data integrity

| ID | Scenario and input | Expected behavior | Coverage status |
|---|---|---|---|
| ING-01 | Adzuna returns a valid posting with a short (~500-character) description. | Ingest the record without inventing missing requirements or responsibilities; flag weak coverage through completeness diagnostics. | Existing test areas: `test_live_ingestion.py`, `test_data_completeness.py`; exact assertion to verify. |
| ING-02 | Two source records represent the same job but differ in capitalization or location formatting. | Surface potential duplication without deleting records solely on a fuzzy match. | Existing test area: `test_duplicate_detector.py`; review normalization cases. |
| ING-03 | An external API fails, times out, or returns a malformed response. | Report the failure; avoid silently storing a partial or fabricated job. | Proposed extension: deterministic mocked HTTP/error cases. |
| ING-04 | Ingestion is rerun for an existing source job ID. | Avoid unintended duplicate canonical rows; preserve expected upsert semantics. | Proposed integration test against temporary SQLite. |

### B. Skill, role, and seniority intelligence

| ID | Scenario and input | Expected behavior | Coverage status |
|---|---|---|---|
| ANA-01 | A job mentions `Python`, `SQL`, and `machine learning` in title/description/requirements. | Normalize recognized skills and avoid double-counting repeated mentions. | Existing test areas: `test_skill_extraction.py`, `test_skill_analysis.py`. |
| ANA-02 | A candidate has a relevant skill but the posting description is sparse. | Show limited evidence; do not equate unmentioned skills with confirmed lack of ability. | Existing test areas: `test_job_matcher.py`, `test_opportunity.py`; specific boundary assertion to verify. |
| ANA-03 | A job title contains `Senior` or `Lead`, while the candidate targets junior/mid-level roles. | Seniority-fit logic should surface a mismatch or penalty rather than treating all ML titles as interchangeable. | Existing test areas: `test_seniority.py`, `test_seniority_fit.py`. |
| ANA-04 | Two postings share similar technical skills but differ in role (`Data Scientist` vs. `Software Engineer`). | Role-fit should distinguish responsibilities, not rank only by keyword overlap. | Existing test area: `test_role_fit.py`; adversarial pair proposed. |
| ANA-05 | The same skill appears in different spellings (`LLM`, `large language models`) or as ambiguous acronyms. | Apply documented vocabulary aliases consistently; avoid unsupported semantic expansion. | Proposed vocabulary regression fixtures. |
| ANA-06 | A description repeats the same matching skill dozens of times. | Repetition must not produce unlimited match credit or falsely imply broad coverage. | Proposed adversarial scoring test. |

### C. Completeness and recommendation diagnostics

| ID | Scenario and input | Expected behavior | Coverage status |
|---|---|---|---|
| DIA-01 | A strong title/role match has a truncated description. | The recommendation identifies evidence gaps; do not interpret the score as high-certainty suitability. | Existing test areas: `test_data_completeness.py`, `test_opportunity_diagnostics.py`. |
| DIA-02 | A posting has a detailed description but little overlap with candidate skills. | Distinguish abundant evidence from poor fit; evidence quality should not automatically mean a high opportunity score. | Proposed paired fixture. |
| DIA-03 | Two jobs receive similar numeric scores but different concerns. | Diagnostic output preserves meaningful strengths, concerns, and recommendation reasons. | Existing test area: `test_opportunity_diagnostics.py`; comparison fixture proposed. |

### D. Source discovery, identity, and extraction

| ID | Scenario and input | Expected behavior | Coverage status |
|---|---|---|---|
| ENR-01 | An employer-owned page matches the company, title, and a trustworthy employer requisition identifier. | Classify according to the validator's explicit rules; do not infer `verified` merely from a plausible title. | Existing test area: `test_source_validator.py`; stronger identity checks proposed. |
| ENR-02 | A third-party page has the same title and company, but only a third-party listing ID. | Treat the page as supplemental and review-required, not as a verified employer requisition. | Existing test areas: `test_source_validator.py`, `test_url_resolver.py`; verify specific assertion. |
| ENR-03 | A URL redirects to a different job, an expired page, or a generic search listing. | Reject or flag the identity mismatch; do not assume the final URL is the intended job. | Proposed redirect/identity integration fixtures. |
| ENR-04 | A page includes valid `JobPosting` JSON-LD with nested or missing optional fields. | Extract available fields, handle absent fields safely, and avoid fabricated requirements. | Existing test area: `test_job_description_extractor.py`. |
| ENR-05 | A job page has no usable JSON-LD but does contain structured HTML sections. | Use structured extraction where supported, retaining requirements and responsibilities separately. | Existing test areas: `test_structured_extractor.py`, `test_structured_extractor_quality.py`. |
| ENR-06 | HTML contains navigation links, salary widgets, marketing text, and repeated boilerplate. | Remove irrelevant fragments and avoid inflating job evidence with site chrome. | Existing test area: `test_structured_extractor_quality.py`; expand with new site layouts. |
| ENR-07 | The posting contains a prompt-injection-like instruction embedded in scraped text. | Treat the text as untrusted job content, never as an instruction to change validation, ranking rules, or program behavior. | Proposed security regression test. |

### E. Persistence and score integrity

| ID | Scenario and input | Expected behavior | Coverage status |
|---|---|---|---|
| DB-01 | The same `(job_id, source_url)` enrichment is saved twice. | Respect the unique constraint and repository upsert behavior rather than producing duplicates. | Existing test area: `test_enrichment_repository.py`; exact duplicate assertion to verify. |
| DB-02 | Two different URLs enrich the same job. | Retain separate provenance records and enable inspection of conflicting evidence. | Proposed repository integration test. |
| DB-03 | An enriched description increases detected skills and score. | Report baseline and provisional values and their deltas without modifying the baseline job object. | Existing test area: `test_score_comparison.py`. |
| DB-04 | Source is `third_party` and validation is `review_required`, even when score rises sharply. | `production_eligible` remains false; no automatic promotion. | Existing test area: `test_score_comparison.py`. |
| DB-05 | Source is `employer` and status is `verified`. | Mark eligible under the current gating rule; eligibility alone does not prove the posting is current or all fields are accurate. | Existing test area: `test_score_comparison.py`. |
| DB-06 | Enriched description is empty or whitespace-only. | Fail validation rather than calculating a misleading comparison. | Existing test area: `test_score_comparison.py`. |
| DB-07 | Score comparison is run against a persisted job. | Confirm database row values, enrichment rows, and session dirty state are unchanged after comparison. | **Proposed extension:** in-memory SQLite persistence test; existing tests establish in-memory immutability only. |

## 4. Observed pilot: why source trust matters

The local pilot used **job ID 18**, a Tempus AI Data Scientist II posting. The canonical Adzuna description was approximately **500 characters**; a third-party Built In Chicago enrichment produced **7,071 characters**. Evidence comparison identified more requirements, responsibilities, and skills. The provisional score comparison reported:

| Metric | Baseline | Provisional | Change |
|---|---:|---:|---:|
| Opportunity score | 60.00 | 85.94 | +25.94 |
| Skill match | 0.00 | 66.67 | +66.67 |
| Evidence score | 0.00 | 86.47 | +86.47 |
| Recommendation | `needs_more_evidence` | `strong_review` | Changed |

**Interpretation:** the original posting lacked enough detail to support technical matching. More text produced a stronger apparent match, **not** a verified improvement in the job's actual suitability. The source was `third_party` / `review_required`, so `production_eligible` remained **false**. The observed example illustrates why score confidence and source authenticity must remain separate concepts. Local job IDs are not portable across databases.

## 5. Limitations and failure modes

| Limitation | Why it matters | Planned mitigation |
|---|---|---|
| Short or incomplete Adzuna descriptions | Underestimates technical evidence and creates false negatives. | Track completeness; enrich selectively; display evidence gaps. |
| Keyword/vocabulary-dependent extraction | Synonyms, context, negation, and emerging tools may be missed or misread. | Maintain aliases, labeled evaluation sets, precision/recall metrics, and contextual checks. |
| Rule-based role/seniority/domain inference | Ambiguous titles and cross-functional jobs can be misclassified. | Evaluate on manually labeled jobs and review borderline cases. |
| Hand-tuned scoring weights | A ranking score is not a calibrated hiring probability or eligibility decision. | Sensitivity analyses, labeled ranking judgments, and calibration studies. |
| Third-party listing identity | A matching title/company does not prove the same requisition or a current opening. | Employer requisition validation, freshness checks, provenance tracking. |
| HTML/JSON-LD extraction drift | Job sites change templates; dynamic content and anti-bot controls reduce reliability. | Fixture-based regression tests, extraction quality checks, manual review fallback. |
| Conflicting enrichment sources | Different sites can publish inconsistent duties, salaries, or dates. | Retain multiple sources, compare fields, flag conflicts; do not silently merge. |
| Unverified evidence inflation | Longer descriptions can raise scores without increasing trustworthiness. | Keep provisional scoring separate and gate promotion by provenance and verification. |
| Database integrity not fully integration-tested | In-memory object tests do not prove persisted rows remain unchanged. | Add SQLite read-only comparison and transaction-level tests. |
| External API variability | Network failures, rate limits, and changing responses make integration tests flaky. | Mocked contract tests and separate live smoke tests. |
| Single-source market sample | An Adzuna-only, Chicago-heavy dataset does not represent the entire US market. | Expand sources and locations; track sampling bias and time windows. |
| Candidate profile is manually curated | Missing or outdated skills affect rankings. | Version profiles, provide evidence for skills, and review changes. |
| No production promotion workflow | `production_eligible` is a gate, not an approval process. | Add explicit human/automated review, audit logs, and freshness criteria. |

## 6. Test execution and acceptance criteria

### Run the full regression suite

```powershell
python -m pytest -q
```

**Last reported result:** `183 passed in 4.99s`. Re-run after any code or documentation-related refactor; this historical result does not guarantee future runs.

### Run focused tests

```powershell
python -m pytest tests/test_data_completeness.py tests/test_duplicate_detector.py tests/test_live_ingestion.py tests/test_live_pipeline.py -q
python -m pytest tests/test_skill_extraction.py tests/test_job_matcher.py tests/test_opportunity.py tests/test_opportunity_diagnostics.py -q
python -m pytest tests/test_source_validator.py tests/test_job_description_extractor.py tests/test_structured_extractor.py tests/test_structured_extractor_quality.py tests/test_url_resolver.py -q
python -m pytest tests/test_enrichment_repository.py tests/test_evidence_comparison.py tests/test_score_comparison.py -q
```

### Acceptance criteria for future scenarios

A new scenario is considered implemented only when it has a deterministic fixture, an assertion tied to the expected behavior, a test name in `tests/`, and a passing result in the full suite. For external sources, distinguish unit tests with mocked pages from optional live smoke tests. Record actual observed outputs separately from illustrative expectations.

### Git and data-safety checks

```powershell
git status --short
git diff --check main...HEAD
git check-ignore -v --no-index data/jobs.db
```

Review changes for embedded credentials and personal data before pushing; checking file extensions alone is insufficient.

## 7. Prioritized next test additions

1. **Persistent read-only comparison (DB-07):** compare before/after SQLite rows and verify the session has no unintended changes.
2. **Source identity and redirect adversarial cases (ENR-02/03):** prove that third-party IDs, stale URLs, and mismatched redirects cannot silently become employer-verified evidence.
3. **Evidence inflation and skill repetition (ANA-06/DIA-02):** ensure description length and keyword repetition do not create unjustified ranking confidence.
4. **Ingestion idempotency and failure recovery (ING-03/04):** prevent duplicate jobs and incomplete writes during API failures.
5. **Security boundary (ENR-07):** verify that instructions embedded in scraped job text are handled strictly as untrusted data.

These additions are recommendations for the next quality milestone, **not existing capabilities or passing tests unless implemented and verified**.
