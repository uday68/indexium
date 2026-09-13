import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.index_service import index_service
from scripts.seed_data import SAMPLE_CORPUS, seed


def rebuild():
    print("Clearing current index...")
    index_service.clear()
    print("Rebuilding index from source data...")
    seed()
    print("Index rebuild completed successfully!")


if __name__ == "__main__":
    rebuild()
