"""Collectors package"""
from .base import BaseCollector
from .web_collector import WebCollector
from .pdf_collector import PDFCollector
from .orchestrator import CollectionOrchestrator

__all__ = [
    "BaseCollector",
    "WebCollector",
    "PDFCollector",
    "CollectionOrchestrator",
]
