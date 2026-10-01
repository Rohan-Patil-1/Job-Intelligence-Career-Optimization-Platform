from datetime import datetime, timezone
from typing import Any

from src.processing.job_schema import JobRecord


def normalize_text(value: Any) -> str | None:
    if value is None:
        return None

    value = str(value).strip()

    if not value:
        return None

    return " ".join(value.split())


def normalize_job(raw_job: dict[str, Any]) -> JobRecord:
    normalized = {
        key: normalize_text(value)
        for key, value in raw_job.items()
    }

    normalized["collected_at"] = (
        raw_job.get("collected_at")
        or datetime.now(timezone.utc).replace(tzinfo=None)
    )

    return JobRecord.model_validate(normalized)