from src.analytics.market import MarketAnalyzer
from src.database.connection import SessionLocal


def inspect_market() -> None:
    session = SessionLocal()

    try:
        analyzer = MarketAnalyzer(session)
        summary = analyzer.analyze()

        print("\n=== Market Summary ===")
        print(f"Total jobs: {summary['total_jobs']}")
        print(f"Unique companies: {summary['unique_companies']}")
        print(f"Unique sources: {summary['unique_sources']}")

    finally:
        session.close()


if __name__ == "__main__":
    inspect_market()