from src.database.connection import SessionLocal
from src.database.repository import JobRepository
from src.analytics.domain_fit import DomainFitAnalyzer


def main():
    preferred_domains = {
        "healthcare",
        "medical_imaging",
        "ai_research",
    }

    analyzer = DomainFitAnalyzer(preferred_domains)

    with SessionLocal() as session:
        jobs = JobRepository(session).get_all()

        print("\n=== Domain Intelligence Report ===")
        print(f"Jobs analyzed: {len(jobs)}")

        domain_counts = {}
        unknown_count = 0

        for job in jobs:
            result = analyzer.analyze(job)

            if result.label == "unknown":
                unknown_count += 1

            for domain in result.detected_domains:
                domain_counts[domain] = (
                    domain_counts.get(domain, 0) + 1
                )

            print("\n" + "=" * 70)
            print(f"{job.title} | {job.company}")
            print(f"Domain fit: {result.score:.2f}")
            print(f"Label: {result.label}")
            print(f"Evidence count: {result.evidence_count}")
            print(f"Evidence level: {result.evidence_level}")
            print(f"Evidence sources: {result.evidence_sources}")
            print(f"Detected: {result.detected_domains}")
            print(f"Preferred: {result.matched_domains}")

            if result.evidence:
                print("Evidence:")
                for domain, keywords in result.evidence.items():
                    print(f"  {domain}: {', '.join(keywords)}")

        print("\n=== Domain Distribution ===")

        for domain, count in sorted(
            domain_counts.items(),
            key=lambda item: item[1],
            reverse=True,
        ):
            print(f"{domain}: {count}")

        print(f"Unknown domain jobs: {unknown_count}")


if __name__ == "__main__":
    main()