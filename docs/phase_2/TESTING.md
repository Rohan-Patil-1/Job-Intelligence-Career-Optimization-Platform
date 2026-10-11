# Testing — Phase 2

## Environment

From the repository root, activate the project's Python virtual environment and install the project dependencies according to the repository setup instructions.

## Full regression suite

```powershell
python -m pytest -q
```

**Recorded Phase 2 baseline:** 183 tests passed in 4.99 seconds in the user's local Windows development environment. Counts and execution time can change as tests are added or run on different machines.

## Focused suites

Analytics, candidate matching, and scoring:

```powershell
python -m pytest tests/test_market_analysis.py tests/test_skill_analysis.py tests/test_skill_extraction.py tests/test_skill_demand.py tests/test_skill_gap.py tests/test_candidate_profile.py tests/test_job_matcher.py tests/test_opportunity.py tests/test_opportunity_diagnostics.py -q
```

Data quality and ingestion:

```powershell
python -m pytest tests/test_data_completeness.py tests/test_duplicate_detector.py tests/test_live_ingestion.py tests/test_live_pipeline.py -q
```

Enrichment and comparisons:

```powershell
python -m pytest tests/test_enrichment_repository.py tests/test_source_validator.py tests/test_job_description_extractor.py tests/test_structured_extractor.py tests/test_structured_extractor_quality.py tests/test_url_resolver.py tests/test_evidence_comparison.py tests/test_score_comparison.py -q
```

## Git checks before publication

```powershell
git status --short
git diff --check main...HEAD
git check-ignore -v --no-index data/jobs.db
git ls-files | Select-String -Pattern '(^|/)\.env($|[.])|\.db$|\.sqlite3?$|\.pem$|\.key$'
```

`.env.example` may appear in the last check; ensure it contains placeholders only. A filename check does **not** prove that source files contain no embedded secrets. Review changed content before publishing.

## External-service caveat

Some ingestion tests or exploratory scripts may depend on the Adzuna API, connectivity, or rate limits. Separate external-service failures from deterministic unit-test failures. The 183-test baseline is a regression signal, not evidence that every external integration works at all times.

## Coverage gaps and future tests

- Verify that score comparison leaves the persisted job record unchanged, not just the in-memory job object.
- Add more adversarial source-validation cases, including misleading third-party identifiers and stale postings.
- Measure skill-extraction precision and recall against labeled examples.
- Test scoring calibration across roles, industries, and description lengths.
- Add integration tests for database migrations and repeated enrichment upserts.

## Phase 2 completion criteria

- Full test suite passes.
- All Phase 2 code is committed.
- Git whitespace checks pass.
- Local database and secrets are excluded from the repository.
- Documentation is committed.
- Feature branch is pushed and reviewed before merging into `main`.

## Scenario-driven engineering documentation

For distinct failure-oriented scenarios, expected behavior, coverage status, the Phase 2 engineering approach, and detailed limitations, see [TEST_SCENARIOS_APPROACH_LIMITATIONS.md](TEST_SCENARIOS_APPROACH_LIMITATIONS.md). The scenario catalog distinguishes existing test areas from proposed tests; it does not imply that all scenarios are implemented.
