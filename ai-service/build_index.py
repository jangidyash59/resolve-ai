"""
Build script — Initialize the vector store from policy documents.
Run this before using the application or evaluating.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config.settings import settings
from src.orchestrator_simple import build_policy_index, search_policies


def build():
    """Build the FAISS vector store from policy documents."""
    print("=" * 60)
    print("  ResolveAI — Policy Vector Store Builder")
    print("=" * 60)
    print()

    # Validate
    settings.validate()

    build_policy_index()

    # Quick test
    print("\nQuick search test: 'return policy for damaged items'")
    results = search_policies("return policy for damaged items", number_of_results=3)
    for i, policy in enumerate(results, 1):
        print(
            f"  {i}. [{policy['citation']}] "
            f"— score: {policy['similarity']:.3f}"
        )

    print("\nVector store built successfully!")
    print(f"   Location: {settings.VECTOR_STORE_PATH}")


if __name__ == "__main__":
    build()
