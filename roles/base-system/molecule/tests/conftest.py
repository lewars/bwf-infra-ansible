import os
import pytest

@pytest.fixture(scope="session", autouse=True)
def print_molecule_env():
    """Print molecule environment variables before any tests run."""
    print("\n========================= MOLECULE TEST ENVIRONMENT =========================")
    print(f"MOLECULE_EPHEMERAL_DIRECTORY: {os.environ.get('MOLECULE_EPHEMERAL_DIRECTORY', 'Not set')}")
    print("===============================================================================n")
