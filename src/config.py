from pathlib import Path

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / ".." / "data"
DATA_DIR = DATA_DIR.resolve()
