"""
Data models and schemas for Insurance Analytics Platform
"""

from typing import List, Dict, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class SourceType(str, Enum):
    """Enumeration of data source types"""
    WEBSITE = "website"
    PDF_REPORT = "pdf_report"
    BROCHURE = "brochure"
    PRESS_RELEASE = "press_release"
    CUSTOMER_REVIEW = "customer_review"
    SOCIAL_MEDIA = "social_media"
    ADVERTISEMENT = "advertisement"
    NEWS = "news"
    BLOG = "blog"
    OTHER = "other"


class Document(BaseModel):
    """Raw document model"""
    id: str = Field(default_factory=lambda: str(datetime.now().timestamp()))
    company: str
    source_type: SourceType
    source_url: str
    publication_date: Optional[datetime] = None
    document_name: str
    raw_text: str
    metadata: Dict[str, Any] = {}
    ingested_at: datetime = Field(default_factory=datetime.now)


class ProcessedChunk(BaseModel):
    """Processed text chunk model"""
    id: str = Field(default_factory=lambda: str(datetime.now().timestamp()))
    document_id: str
    company: str
    source_type: SourceType
    source_url: str
    publication_date: Optional[datetime]
    document_name: str
    chunk_index: int
    text: str
    chunk_size: int
    metadata: Dict[str, Any] = {}
    processed_at: datetime = Field(default_factory=datetime.now)


class BrandPositioning(BaseModel):
    """Brand positioning model"""
    brand: str
    positioning_statement: str
    main_claims: List[str] = []
    trust_signals: List[str] = []
    emotional_themes: List[str] = []
    target_segments: List[str] = []
    product_focus: List[str] = []
    key_differentiators: List[str] = []
    market_position: Optional[str] = None
    confidence: float = 0.0
    supporting_evidence: List[str] = []


class PerceptionDimension(BaseModel):
    """Perception dimension definition"""
    dimension_name: str
    description: str
    evidence_keywords: List[str] = []
    scoring_method: str
    importance_weight: float = 1.0


class PerceptionScore(BaseModel):
    """Perception score for a company on a dimension"""
    company: str
    dimension: str
    score: float  # 0-10
    rationale: str
    evidence: List[str] = []
    supporting_snippets: List[str] = []
    confidence: float = 0.0


class CompanyProfile(BaseModel):
    """Complete brand profile for a company"""
    company: str
    positioning: BrandPositioning
    perception_scores: Dict[str, float] = {}  # dimension -> score
    total_documents_analyzed: int = 0
    analysis_timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = {}


class BenchmarkComparison(BaseModel):
    """Benchmark comparison between companies"""
    comparison_id: str
    companies: List[str]
    dimension: str
    company_scores: Dict[str, float] = {}  # company -> score
    winner: Optional[str] = None
    gap_analysis: Dict[str, float] = {}
    insights: List[str] = []


class CustomerReviewSentiment(BaseModel):
    """Customer review sentiment analysis"""
    company: str
    total_reviews_analyzed: int
    overall_sentiment: float  # -1 to 1
    sentiment_distribution: Dict[str, int]  # positive, negative, neutral
    top_praise_topics: List[Dict[str, Any]] = []
    top_complaint_topics: List[Dict[str, Any]] = []
    topic_sentiments: Dict[str, float] = {}


class InsightFindings(BaseModel):
    """Executive-level insights"""
    insight_id: str
    category: str  # positioning_gap, competitive_threat, differentiation_opportunity, etc.
    title: str
    description: str
    companies_involved: List[str]
    evidence: List[str]
    recommendations: List[str] = []
    priority: str = "medium"  # high, medium, low
    impact_score: float = 0.0  # 0-10


class Report(BaseModel):
    """Comprehensive report model"""
    report_id: str = Field(default_factory=lambda: str(datetime.now().timestamp()))
    report_type: str  # brand_profile, benchmark, executive_summary
    title: str
    generated_at: datetime = Field(default_factory=datetime.now)
    companies_included: List[str]
    analysis_summary: Dict[str, Any]
    detailed_findings: List[Dict[str, Any]] = []
    recommendations: List[str] = []
    metadata: Dict[str, Any] = {}


__all__ = [
    "SourceType",
    "Document",
    "ProcessedChunk",
    "BrandPositioning",
    "PerceptionDimension",
    "PerceptionScore",
    "CompanyProfile",
    "BenchmarkComparison",
    "CustomerReviewSentiment",
    "InsightFindings",
    "Report",
]
