import json

import requests

from src.config import ADZUNA_APP_ID, ADZUNA_APP_KEY


BASE_URL = "https://api.adzuna.com/v1/api/jobs"


def main() -> None:
    url = f"{BASE_URL}/us/search/1"

    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "what": "data scientist",
        "where": "Chicago",
        "results_per_page": 1,
        "content-type": "application/json",
    }

    response = requests.get(
        url,
        params=params,
        timeout=30,
    )
    response.raise_for_status()

    data = response.json()

    results = data.get("results", [])

    if not results:
        print("No jobs returned.")
        return

    job = results[0]

    print("\n=== RAW ADZUNA JOB ===")
    print(json.dumps(job, indent=2))

    print("\n=== AVAILABLE FIELDS ===")

    for key in sorted(job.keys()):
        value = job[key]

        if isinstance(value, str):
            print(
                f"{key:<25} "
                f"type=str "
                f"length={len(value)}"
            )
        else:
            print(
                f"{key:<25} "
                f"type={type(value).__name__}"
            )

    description = job.get("description") or ""

    print("\n=== DESCRIPTION ===")
    print(f"Length: {len(description)}")
    print(description)

    print("\n=== REDIRECT URL ===")
    print(job.get("redirect_url"))


if __name__ == "__main__":
    main()