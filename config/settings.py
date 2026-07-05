"""
Configuration management for Insurance Analytics Platform
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
EMBEDDINGS_DIR = DATA_DIR / "embeddings"
OUTPUT_DIR = DATA_DIR / "outputs"
LOGS_DIR = BASE_DIR / "logs"
CONFIG_DIR = BASE_DIR / "config"

# Ensure directories exist
for directory in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, EMBEDDINGS_DIR, OUTPUT_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Local LLM Configuration (Free, No API costs)
# Supports: mistral, neural-chat, llama2, dolphin-mixtral, etc.
LOCAL_LLM_MODEL = os.getenv("LOCAL_LLM_MODEL", "mistral")  # Fast and capable
LOCAL_LLM_HOST = os.getenv("LOCAL_LLM_HOST", "http://localhost:11434")
LOCAL_LLM_TEMPERATURE = float(os.getenv("LOCAL_LLM_TEMPERATURE", "0.7"))
LOCAL_LLM_TOP_K = int(os.getenv("LOCAL_LLM_TOP_K", "40"))
LOCAL_LLM_TOP_P = float(os.getenv("LOCAL_LLM_TOP_P", "0.9"))

# Local Embedding Configuration (Free, No API costs)
# Using sentence-transformers (runs locally)
LOCAL_EMBEDDING_MODEL = os.getenv("LOCAL_EMBEDDING_MODEL", "all-MiniLM-L6-v2")  # Fast & good
EMBEDDING_DEVICE = os.getenv("EMBEDDING_DEVICE", "cpu").lower()
if EMBEDDING_DEVICE == "gpu":
    EMBEDDING_DEVICE = "cuda"

# Database Configuration
CHROMADB_PATH = os.getenv("CHROMADB_PATH", str(EMBEDDINGS_DIR))
CACHE_ENABLED = os.getenv("CACHE_ENABLED", "true").lower() == "true"
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Data Collection Settings
PLAYWRIGHT_HEADLESS = os.getenv("PLAYWRIGHT_HEADLESS", "true").lower() == "true"
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", str(LOGS_DIR / "app.log"))

# Output Configuration
OUTPUT_FORMAT = os.getenv("OUTPUT_FORMAT", "json")
REPORT_OUTPUT_PATH = os.getenv("REPORT_OUTPUT_PATH", str(OUTPUT_DIR))

# Project Configuration
PROJECT_NAME = os.getenv("PROJECT_NAME", "Insurance Brand Analytics")
VERSION = os.getenv("VERSION", "1.0.0")

# Insurance Companies Configuration
COMPANIES = {
    "HDFC Life": {
        "full_name": "HDFC Life Insurance Company Limited",
        "website": "https://www.hdfclife.com",
        "founded": 2000,
    },
    "LIC": {
        "full_name": "Life Insurance Corporation of India",
        "website": "https://www.licindia.in",
        "founded": 1956,
    },
    "ICICI Prudential Life": {
        "full_name": "ICICI Prudential Life Insurance Company Limited",
        "website": "https://www.iciciprulife.com",
        "founded": 2000,
    },
    "SBI Life": {
        "full_name": "SBI Life Insurance Company Limited",
        "website": "https://www.sbilife.co.in",
        "founded": 2009,
    },
}

# Data Collection Configuration
DATA_SOURCES = {
    "website": {
        "enabled": True,
        "priority": 1,
        "description": "Company main website and product pages"
    },
    "annual_reports": {
        "enabled": True,
        "priority": 2,
        "description": "Annual reports and investor presentations"
    },
    "brochures": {
        "enabled": True,
        "priority": 3,
        "description": "Product brochures and documentation"
    },
    "press_releases": {
        "enabled": True,
        "priority": 4,
        "description": "Press releases and news"
    },
    "reviews": {
        "enabled": True,
        "priority": 5,
        "description": "Customer reviews and ratings"
    }
}

# Embedding Configuration
EMBEDDING_CHUNK_SIZE = 500
EMBEDDING_OVERLAP = 50
EMBEDDING_BATCH_SIZE = 100

# Analysis Configuration
PERCEPTION_DIMENSIONS_COUNT = 8
MIN_EVIDENCE_THRESHOLD = 0.6
CONFIDENCE_THRESHOLD = 0.7

# Benchmarking Configuration
BENCHMARK_METRICS = [
    "trust",
    "innovation",
    "customer_service",
    "digital_experience",
    "affordability",
    "transparency",
    "security",
    "brand_legacy"
]

# RAG Configuration
RAG_TOP_K = 5
RAG_RELEVANCE_THRESHOLD = 0.5

# API Configuration
API_HOST = "0.0.0.0"
API_PORT = 8000
API_WORKERS = 4

# Dashboard Configuration
DASHBOARD_PORT = 8501

__all__ = [
    "BASE_DIR",
    "DATA_DIR",
    "RAW_DATA_DIR",
    "PROCESSED_DATA_DIR",
    "EMBEDDINGS_DIR",
    "OUTPUT_DIR",
    "LOGS_DIR",
    "COMPANIES",
    "DATA_SOURCES",
    "BENCHMARK_METRICS",
    "LOCAL_LLM_MODEL",
    "LOCAL_LLM_HOST",
    "LOCAL_LLM_TEMPERATURE",
    "LOCAL_LLM_TOP_K",
    "LOCAL_LLM_TOP_P",
    "LOCAL_EMBEDDING_MODEL",
    "EMBEDDING_DEVICE",
    "CHROMADB_PATH",
    "PLAYWRIGHT_HEADLESS",
    "REQUEST_TIMEOUT",
    "MAX_RETRIES",
    "LOG_LEVEL",
    "LOG_FILE",
]
