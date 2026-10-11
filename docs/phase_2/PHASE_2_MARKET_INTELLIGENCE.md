# Phase 2 — Market Analysis & Role Intelligence

## Purpose

Phase 2 extends the job ingestion and persistence foundation from Phase 1 into a local, testable job-market intelligence system. It analyzes stored job postings, compares them with a candidate profile, and generates evidence-aware opportunity rankings.

## Architecture

```text
Job sources (Adzuna)
        |
        v
Normalization and SQLite job repository (Phase 1)
        |
        +--> Market, skills, seniority and domain analytics
        |
        +--> Data completeness and duplicate diagnostics
        |
        +--> Candidate profile and opportunity scoring
        |
        +--> Enrichment source discovery / validation / extraction
                    |
                    v
             job_enrichments (separate from jobs)
                    |
                    v
             Evidence and provisional score comparisons
```

## Implemented capabilities

### Market and skills intelligence

The `src/analytics/` package provides market-level inspection and skill analysis. Its components include `market.py`, `skills.py`, `skill_extractor.py`, `skill_vocabulary.py`, `skill_demand.py`, and `skill_gap.py`. Domain and seniority modules identify role-related evidence, while CLI inspection modules expose analysis outputs.

### Candidate matching and opportunity ranking

The `src/profile/` package defines a candidate profile and a default profile configuration. `job_matcher.py`, `role_fit.py`, `seniority_fit.py`, `domain_fit.py`, and `opportunity.py` evaluate job-to-candidate alignment. `opportunity_diagnostics.py` provides recommendation categories, strengths, concerns, and evidence gaps.

The scoring system combines technical matching, role fit, seniority fit, and domain evidence. It distinguishes a ranking score from the amount of supporting evidence. The specific weights and multipliers are implementation details defined in `src/analytics/opportunity.py` and should be updated here if that implementation changes.

### Data quality

`data_completeness.py` and `duplicate_detector.py` identify incomplete or potentially duplicate postings. Diagnostic scripts inspect source data, raw descriptions, and description lengths. Ingestion improvements and tests remain in `src/ingestion/` and `tests/`.

### Evidence-aware enrichment

The enrichment pipeline can discover, validate, and extract additional job-posting evidence. Its results are stored separately from original postings and compared without silently replacing the original job description. See [ENRICHMENT_PIPELINE.md](ENRICHMENT_PIPELINE.md).

## Validation

The user-reported full regression run completed successfully with **183 tests passing** (`python -m pytest -q`). This is the Phase 2 test baseline, not a guarantee of production reliability or coverage of every external job board.

## Scope and limitations

- The current job corpus was gathered from Adzuna and may contain short descriptions, duplicates, or incomplete metadata.
- Skill extraction is vocabulary-dependent; extraction counts and scoring-engine skill counts may differ.
- Matching and ranking are decision-support signals, not guarantees of candidate eligibility, hiring probability, or compensation.
- Third-party or unverified enrichment is provisional and must not be promoted automatically to verified production evidence.
- Source discovery and extraction can be affected by changing page structures, redirects, access restrictions, and source availability.
- Phase 2 does not implement automated job applications or a production deployment.

## Useful commands

Run the full test suite:

```powershell
python -m pytest -q
```

Inspect the market and candidate rankings:

```powershell
python -m src.analytics.inspect_market
python -m src.analytics.inspect_opportunities
python -m src.analytics.inspect_review_priorities
```

For database initialization and enrichment comparison commands, see [ENRICHMENT_PIPELINE.md](ENRICHMENT_PIPELINE.md).

## Next phase

The next phase should be scoped independently, using this tested analytics and enrichment foundation. Avoid treating provisional enrichment as authoritative until an explicit verification policy is implemented.
