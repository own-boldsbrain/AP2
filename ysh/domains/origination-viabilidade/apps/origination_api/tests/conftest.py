import os
import sys
from pathlib import Path

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("NATS_URL", "nats://localhost:4222")

sys.path.append(str(Path(__file__).resolve().parents[1]))
