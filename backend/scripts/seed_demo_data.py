from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.db import SessionLocal
from app.services.seeding import seed_demo_data


def main() -> None:
    with SessionLocal() as db:
        result = seed_demo_data(db)

    print("Seeded demo salon data.")
    print(f"Services created: {result['services_created']}")
    print(f"Business-hour rows written: {result['business_hours_written']}")


if __name__ == "__main__":
    main()
