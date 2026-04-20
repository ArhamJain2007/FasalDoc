"""
Standalone script to populate disease + treatment data.
Run once after running Alembic migrations:
  python scripts/seed_diseases.py
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.db.session import AsyncSessionLocal
from app.db.init_db import init_db
import structlog

logger = structlog.get_logger()


async def main() -> None:
    """Connect to DB and run the seed routine."""
    print("Connecting to database and seeding disease/treatment data...")
    async with AsyncSessionLocal() as db:
        await init_db(db)
    print("✓ Seeding complete.")


if __name__ == "__main__":
    asyncio.run(main())
