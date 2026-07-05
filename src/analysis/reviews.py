"""
Customer review sentiment and topic analysis
"""

from typing import List, Dict, Optional, Any
import re
from collections import Counter
from src.utils.logger import get_logger
from src.utils.models import CustomerReviewSentiment

try:
    from textblob import TextBlob
except ImportError:
    TextBlob = None

logger = get_logger("analysis.reviews")


class ReviewAnalyzer:
    """Analyze customer reviews for sentiment and topics"""
    
    def __init__(self):
        self.common_praise_keywords = [
            'excellent', 'great', 'wonderful', 'fantastic', 'amazing', 'love',
            'best', 'perfect', 'highly recommend', 'satisfied', 'happy', 'impressed',
            'professional', 'helpful', 'quick', 'efficient', 'trustworthy'
        ]
        
        self.common_complaint_keywords = [
            'poor', 'bad', 'terrible', 'hate', 'worst', 'frustrated', 'disappointed',
            'slow', 'unhelpful', 'unprofessional', 'expensive', 'useless', 'avoid',
            'scam', 'fraud', 'misleading', 'complicated', 'confusing'
        ]
    
    def analyze_reviews(self, reviews: List[str], company: str) -> CustomerReviewSentiment:
        """Analyze collection of reviews"""
        logger.info(f"Analyzing {len(reviews)} reviews for {company}")
        
        sentiments = []
        praise_topics = Counter()
        complaint_topics = Counter()
        
        for review in reviews:
            sentiment = self._analyze_single_review(review)
            sentiments.append(sentiment)
            
            # Extract topics
            if sentiment > 0.2:
                topics = self._extract_praise_topics(review)
                praise_topics.update(topics)
            elif sentiment < -0.2:
                topics = self._extract_complaint_topics(review)
                complaint_topics.update(topics)
        
        # Calculate aggregates
        overall_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
        
        positive_count = len([s for s in sentiments if s > 0.2])
        negative_count = len([s for s in sentiments if s < -0.2])
        neutral_count = len(sentiments) - positive_count - negative_count
        
        return CustomerReviewSentiment(
            company=company,
            total_reviews_analyzed=len(reviews),
            overall_sentiment=overall_sentiment,
            sentiment_distribution={
                'positive': positive_count,
                'negative': negative_count,
                'neutral': neutral_count
            },
            top_praise_topics=[
                {'topic': topic, 'count': count}
                for topic, count in praise_topics.most_common(5)
            ],
            top_complaint_topics=[
                {'topic': topic, 'count': count}
                for topic, count in complaint_topics.most_common(5)
            ]
        )
    
    def _analyze_single_review(self, review: str) -> float:
        """Analyze sentiment of single review (-1 to 1)"""
        if not review or len(review.strip()) == 0:
            return 0
        
        # Simple keyword-based sentiment
        positive_words = sum(1 for word in self.common_praise_keywords if word.lower() in review.lower())
        negative_words = sum(1 for word in self.common_complaint_keywords if word.lower() in review.lower())
        
        total_sentiment_words = positive_words + negative_words
        
        if total_sentiment_words == 0:
            return 0
        
        sentiment_score = (positive_words - negative_words) / total_sentiment_words
        return min(1.0, max(-1.0, sentiment_score))
    
    def _extract_praise_topics(self, review: str) -> List[str]:
        """Extract praise topics from review"""
        topics = []
        
        praise_patterns = {
            'customer_service': ['service', 'support', 'help', 'friendly', 'responsive'],
            'speed': ['quick', 'fast', 'quick', 'efficient', 'prompt'],
            'products': ['product', 'plan', 'policy', 'offering'],
            'trust': ['trustworthy', 'reliable', 'honest', 'transparent'],
            'value': ['value', 'affordable', 'worth', 'good price'],
        }
        
        review_lower = review.lower()
        for topic, keywords in praise_patterns.items():
            if any(kw in review_lower for kw in keywords):
                topics.append(topic)
        
        return topics
    
    def _extract_complaint_topics(self, review: str) -> List[str]:
        """Extract complaint topics from review"""
        topics = []
        
        complaint_patterns = {
            'claim_process': ['claim', 'settlement', 'rejection', 'denied', 'difficult'],
            'customer_service': ['service', 'support', 'unhelpful', 'rude', 'slow'],
            'pricing': ['expensive', 'premium', 'cost', 'overpriced', 'hidden'],
            'products': ['product', 'plan', 'policy', 'limited', 'poor'],
            'transparency': ['misleading', 'hidden', 'unclear', 'confusing', 'ambiguous'],
        }
        
        review_lower = review.lower()
        for topic, keywords in complaint_patterns.items():
            if any(kw in review_lower for kw in keywords):
                topics.append(topic)
        
        return topics


__all__ = ["ReviewAnalyzer"]
