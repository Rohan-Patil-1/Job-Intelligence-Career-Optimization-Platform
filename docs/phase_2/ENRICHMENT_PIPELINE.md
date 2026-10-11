# Enrichment Pipeline — Phase 2

## Objective

Some job APIs provide shortened descriptions. Enrichment collects supplemental evidence from candidate posting URLs, evaluates its provenance, and supports comparisons against the original record **without silently changing the original job**.

## Pipeline

```text
Stored job
  -> enrichment queue / source discovery
  -> URL resolution
  -> source validation
  -> JSON-LD or structured HTML extraction
  -> extracted job details and quality checks
  -> job_enrichments persistence
  -> evidence comparison
  -> provisional opportunity-score comparison
```

## Source discovery and validation

Relevant modules in `src/enrichment/` include:

- `enrichment_queue.py` and `source_discovery.py`: identify jobs and candidate supplemental sources.
- `url_resolver.py`: resolve or inspect job posting URLs.
- `source_validator.py`: assess source identity and validation status.
- `inspect_enrichment_queue.py`, `inspect_job_urls.py`, and `inspect_source_discovery.py`: diagnostic entry points.

Source identity and validation must be treated separately. A third-party listing is not automatically equivalent to an employer-owned job posting, even if the title and company appear to match. A listing identifier from a third-party site is not necessarily the employer requisition ID.

## Extraction

- `job_description_extractor.py` handles structured `JobPosting` data such as JSON-LD.
- `structured_extractor.py` extracts and cleans content from page structure, including descriptions, requirements, responsibilities, and skills.
- `run_enrichment_pilot.py` supports an exploratory enrichment workflow.

Extraction quality depends on the source page and may need manual review.

## Persistence

The SQLAlchemy `JobEnrichment` model in `src/database/models.py` stores supplemental evidence in the **`job_enrichments`** table. `src/database/enrichment_repository.py` manages access and upserts. It stores provenance fields such as source URL, source type, validation status, extraction method, and extracted content. The original `jobs` table remains the baseline record.

Initialize tables non-destructively with:

```powershell
python -m src.database.init_db
```

Database files such as `data/jobs.db` are local and ignored by Git. Do not commit raw databases or secrets.

## Evidence comparison

`evidence_comparison.py` and `run_evidence_comparison.py` compare coverage between the baseline and enriched descriptions. For a previously enriched job, run:

```powershell
python -m src.enrichment.run_evidence_comparison --job-id 18
```

The job ID above refers to a local example and is not portable across databases.

## Provisional score comparison

`score_comparison.py` constructs a transient job object with the enriched description, computes baseline and provisional opportunity scores, and reports differences in ranking and matched skills. The comparison does not write a replacement score or overwrite the baseline description.

```powershell
python -m src.enrichment.run_score_comparison --job-id 18
```

The user-reported example for a Tempus AI posting produced a baseline opportunity score of **60.00** and a provisional score of **85.94**, a **+25.94** difference. The supplemental source was classified as `third_party` with `review_required` validation and **was not production eligible**. This illustrates how additional text can improve apparent matching while source trust remains unresolved.

## Trust boundary

The comparison implementation considers enrichment production-eligible only when its source type is `employer` and its validation status is `verified`. This is a gating rule, not proof that all verified-source content is factually accurate. The current CLI is an exploratory, read-only comparison and should not be interpreted as an automatic promotion mechanism.

## Known limitations

- Structured extraction and scoring use different vocabularies and may report different skill counts.
- Job pages may change, block automated access, or contain stale information.
- Matching titles and companies alone is insufficient to establish posting identity.
- The enriched description is a comparison input, not a verified replacement for the canonical job record.
- Human review or stronger employer-source verification may be needed before using enrichment for production ranking.

## Related tests

```powershell
python -m pytest tests/test_enrichment_repository.py tests/test_job_description_extractor.py tests/test_source_validator.py tests/test_structured_extractor.py tests/test_structured_extractor_quality.py tests/test_url_resolver.py tests/test_evidence_comparison.py tests/test_score_comparison.py -q
```
