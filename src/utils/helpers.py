"""
Utility helper functions for Insurance Analytics Platform
"""

import json
import hashlib
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

def clean_text(text: str) -> str:
    """Clean and normalize text"""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    # Remove special characters but keep punctuation
    text = re.sub(r'[^\w\s.,;:!?\'"&-]', '', text)
    return text


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """Split text into overlapping chunks"""
    if not text or chunk_size <= 0:
        return []
    
    chunks = []
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    current_chunk = ""
    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= chunk_size:
            current_chunk += " " + sentence if current_chunk else sentence
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            # Create overlap
            current_chunk = current_chunk[-overlap:] + " " + sentence if len(current_chunk) > overlap else sentence
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks


def extract_domain(url: str) -> str:
    """Extract domain from URL"""
    parsed = urlparse(url)
    return parsed.netloc or parsed.path


def generate_id(content: str, prefix: str = "") -> str:
    """Generate unique ID from content hash"""
    hash_obj = hashlib.md5(content.encode())
    hash_id = hash_obj.hexdigest()[:12]
    return f"{prefix}_{hash_id}" if prefix else hash_id


def save_json(data: Dict[str, Any], filepath: Path) -> None:
    """Save data as JSON file"""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)


def load_json(filepath: Path) -> Dict[str, Any]:
    """Load JSON file"""
    if not filepath.exists():
        return {}
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_jsonl(data: List[Dict[str, Any]], filepath: Path) -> None:
    """Save data as JSONL file"""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        for record in data:
            f.write(json.dumps(record, ensure_ascii=False, default=str) + '\n')


def load_jsonl(filepath: Path) -> List[Dict[str, Any]]:
    """Load JSONL file"""
    data = []
    if not filepath.exists():
        return data
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line))
    return data


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for filesystem"""
    return re.sub(r'[^a-zA-Z0-9_-]', '_', filename)


def merge_dicts(dict1: Dict, dict2: Dict, overwrite: bool = False) -> Dict:
    """Recursively merge two dictionaries"""
    result = dict1.copy()
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value, overwrite)
        elif key not in result or overwrite:
            result[key] = value
    return result


def calculate_similarity(text1: str, text2: str) -> float:
    """Simple text similarity using Jaccard index"""
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = len(words1 & words2)
    union = len(words1 | words2)
    
    return intersection / union if union > 0 else 0.0


def deduplicate_texts(texts: List[str], threshold: float = 0.9) -> List[str]:
    """Remove similar texts based on threshold"""
    if not texts:
        return []
    
    unique_texts = [texts[0]]
    
    for text in texts[1:]:
        is_duplicate = False
        for unique_text in unique_texts:
            if calculate_similarity(text, unique_text) > threshold:
                is_duplicate = True
                break
        if not is_duplicate:
            unique_texts.append(text)
    
    return unique_texts


def format_timestamp(dt: Optional[datetime] = None) -> str:
    """Format datetime to ISO string"""
    if dt is None:
        dt = datetime.now()
    return dt.isoformat()


def parse_timestamp(timestamp_str: str) -> datetime:
    """Parse ISO format timestamp"""
    return datetime.fromisoformat(timestamp_str)


__all__ = [
    "clean_text",
    "chunk_text",
    "extract_domain",
    "generate_id",
    "save_json",
    "load_json",
    "save_jsonl",
    "load_jsonl",
    "sanitize_filename",
    "merge_dicts",
    "calculate_similarity",
    "deduplicate_texts",
    "format_timestamp",
    "parse_timestamp",
]
