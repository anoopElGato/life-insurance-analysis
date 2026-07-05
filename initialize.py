"""
System initialization script for the local LLM setup.
"""

import json
import sys
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config.settings import (  # noqa: E402
    BASE_DIR,
    CHROMADB_PATH,
    COMPANIES,
    DATA_DIR,
    EMBEDDING_DEVICE,
    EMBEDDINGS_DIR,
    LOCAL_EMBEDDING_MODEL,
    LOCAL_LLM_HOST,
    LOCAL_LLM_MODEL,
    LOGS_DIR,
    OUTPUT_DIR,
    PROCESSED_DATA_DIR,
    RAW_DATA_DIR,
)

def check_environment():
    """Check and validate environment."""
    print("\n" + "=" * 80)
    print("ENVIRONMENT CHECK")
    print("=" * 80)

    checks_passed = True

    print(f"\n[OK] Python Version: {sys.version}")

    print("\nLocal LLM Configuration:")
    print(f"  [OK] Model: {LOCAL_LLM_MODEL}")
    print(f"  [OK] Host: {LOCAL_LLM_HOST}")
    print(f"  [OK] Embedding Model: {LOCAL_EMBEDDING_MODEL}")
    print(f"  [OK] Embedding Device: {EMBEDDING_DEVICE}")

    try:
        import requests

        response = requests.get(f"{LOCAL_LLM_HOST.rstrip('/')}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            model_names = [model.get("name", "") for model in models]
            model_available = any(
                name == LOCAL_LLM_MODEL or name.startswith(f"{LOCAL_LLM_MODEL}:")
                for name in model_names
            )

            print("  [OK] Ollama Server: Running")
            if model_available:
                print(f"  [OK] Ollama Model: {LOCAL_LLM_MODEL} is installed")
            else:
                print(f"  [WARN] Ollama Model: {LOCAL_LLM_MODEL} not found locally")
                print(f"    -> Run: ollama pull {LOCAL_LLM_MODEL}")
                checks_passed = False
        else:
            print(f"  [FAIL] Ollama Server: HTTP {response.status_code}")
            checks_passed = False
    except Exception as exc:
        print(f"  [FAIL] Ollama Server: Not reachable at {LOCAL_LLM_HOST}")
        print("    -> Start Ollama, then run: ollama serve")
        print(f"    -> Details: {exc}")
        checks_passed = False

    print("\nDirectory Structure:")
    directories = {
        "Base": BASE_DIR,
        "Data": DATA_DIR,
        "Raw": RAW_DATA_DIR,
        "Processed": PROCESSED_DATA_DIR,
        "Embeddings": EMBEDDINGS_DIR,
        "Outputs": OUTPUT_DIR,
        "Logs": LOGS_DIR,
    }

    for name, path in directories.items():
        exists = path.exists()
        status = "[OK]" if exists else "[CREATE]"
        print(f"  {status} {name}: {path}")
        if not exists:
            path.mkdir(parents=True, exist_ok=True)
            print("    -> Created")

    return checks_passed


def check_dependencies():
    """Check if required packages are installed."""
    print("\n" + "=" * 80)
    print("DEPENDENCY CHECK")
    print("=" * 80)

    required_packages = [
        "requests",
        "bs4",
        "pdfplumber",
        "chromadb",
        "sentence_transformers",
        "ollama",
        "pandas",
        "plotly",
        "streamlit",
    ]

    all_installed = True

    for package in required_packages:
        try:
            __import__(package)
            print(f"[OK] {package}")
        except ImportError as exc:
            print(f"[FAIL] {package} - IMPORT FAILED")
            print(f"       {exc}")
            all_installed = False

    if not all_installed:
        print("\nTo install or repair missing packages, run:")
        print("  pip install -r requirements.txt")

    return all_installed


def initialize_database():
    """Initialize vector database."""
    print("\n" + "=" * 80)
    print("DATABASE INITIALIZATION")
    print("=" * 80)

    try:
        from src.embeddings.vector_db import VectorDatabase

        print("Initializing ChromaDB...")
        vector_db = VectorDatabase(load_embedding_model=False)

        print(f"[OK] Database initialized at: {vector_db.db_path}")
        print(f"[OK] Collections: {vector_db.list_collections()}")

        return True

    except Exception as exc:
        print(f"[FAIL] Error initializing database: {exc}")
        return False


def check_embedding_model():
    """Check whether the configured sentence-transformers model can be loaded."""
    print("\n" + "=" * 80)
    print("EMBEDDING MODEL CHECK")
    print("=" * 80)

    try:
        from src.embeddings.vector_db import EmbeddingManager

        print(f"Loading embedding model: {LOCAL_EMBEDDING_MODEL} on {EMBEDDING_DEVICE}")
        EmbeddingManager()
        print("[OK] Embedding model loaded")
        return True
    except Exception as exc:
        print(f"[FAIL] Error loading embedding model: {exc}")
        print("\nIf this is the first run, sentence-transformers must download the model once.")
        print("Run this from an internet-enabled shell:")
        print(f"  python -c \"from sentence_transformers import SentenceTransformer; SentenceTransformer('{LOCAL_EMBEDDING_MODEL}')\"")
        print("\nIf you do not have an NVIDIA CUDA setup, set this in .env:")
        print("  EMBEDDING_DEVICE=cpu")
        return False


def create_default_config():
    """Create default configuration file."""
    print("\n" + "=" * 80)
    print("CONFIGURATION SETUP")
    print("=" * 80)

    config = {
        "companies": COMPANIES,
        "initialized_at": str(Path(".")),
        "llm": {
            "provider": "ollama",
            "model": LOCAL_LLM_MODEL,
            "host": LOCAL_LLM_HOST,
        },
        "embeddings": {
            "provider": "sentence-transformers",
            "model": LOCAL_EMBEDDING_MODEL,
            "device": EMBEDDING_DEVICE,
            "chromadb_path": CHROMADB_PATH,
        },
        "features": {
            "web_collection": True,
            "pdf_collection": True,
            "rag_analysis": True,
            "dimension_discovery": True,
            "benchmarking": True,
            "reporting": True,
            "dashboard": True,
        },
    }

    config_file = OUTPUT_DIR / "config.json"

    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)

    print(f"[OK] Configuration saved to: {config_file}")

    return True


def print_next_steps():
    """Print next steps."""
    print("\n" + "=" * 80)
    print("INITIALIZATION COMPLETE")
    print("=" * 80)

    print(f"""
Next Steps:

1. VERIFY LOCAL LLM
   - Keep Ollama running in the background
   - If needed, pull the configured model: ollama pull {LOCAL_LLM_MODEL}
   - Optional: edit .env to change LOCAL_LLM_MODEL or LOCAL_LLM_HOST

2. COLLECT DATA
   - Run: python -c "from src.collectors.orchestrator import CollectionOrchestrator; o = CollectionOrchestrator(); o.setup_default_collectors(); o.collect_all()"
   - Or use: python main.py (runs complete pipeline)

3. RUN ANALYSIS
   - Complete Pipeline: python main.py
   - Individual components: see examples/pipeline_example.py
   - Dashboard: streamlit run src/dashboard/app.py

4. VIEW RESULTS
   - Reports: data/outputs/*.json and *.md
   - Dashboard: http://localhost:8501
   - Logs: logs/app.log

5. CUSTOMIZE
   - Add new companies in config/settings.py
   - Add new data sources in src/collectors/
   - Modify perception dimensions in config/settings.py

For detailed documentation, see README.md
For local LLM setup, see LOCAL_LLM_SETUP.md
For examples, see examples/pipeline_example.py
    """)


def main():
    """Main initialization."""
    print("\n")
    print("=" * 80)
    print("INSURANCE BRAND ANALYTICS - LOCAL LLM INITIALIZATION".center(80))
    print("=" * 80)

    env_ok = check_environment()
    deps_ok = check_dependencies()

    if not deps_ok:
        print("\n[WARN] Some dependencies are missing. Install them with:")
        print("  pip install -r requirements.txt")
        return False

    db_ok = initialize_database()
    embeddings_ok = check_embedding_model()
    config_ok = create_default_config()

    if env_ok and deps_ok and db_ok and embeddings_ok and config_ok:
        print_next_steps()
        print("\n[OK] System initialized successfully!")
        return True

    print("\n[FAIL] Initialization encountered some issues. Please review above.")
    return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
