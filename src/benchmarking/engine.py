"""
Competitor benchmarking and comparison engine
"""

from typing import List, Dict, Optional, Any
import json
from src.utils.logger import get_logger
from src.utils.models import (
    PerceptionScore, BrandPositioning, BenchmarkComparison, InsightFindings
)
from src.rag.analyzer import RAGAnalyzer
from src.rag.retriever import DocumentRetriever

logger = get_logger("benchmarking.engine")


class BenchmarkEngine:
    """Generate competitive benchmarks and insights"""
    
    def __init__(self, analyzer: RAGAnalyzer, retriever: DocumentRetriever):
        self.analyzer = analyzer
        self.retriever = retriever
    
    def create_dimension_benchmark(
        self,
        dimension: str,
        company_scores: Dict[str, PerceptionScore]
    ) -> BenchmarkComparison:
        """Create benchmark for a specific dimension"""
        logger.info(f"Creating benchmark for dimension: {dimension}")
        
        companies = list(company_scores.keys())
        scores_dict = {company: score.score for company, score in company_scores.items()}
        
        # Find winner
        winner = max(scores_dict, key=scores_dict.get)
        
        # Calculate gaps
        gaps = self._calculate_gaps(scores_dict, winner)
        
        # Generate insights
        insights = self._generate_dimension_insights(dimension, company_scores)
        
        return BenchmarkComparison(
            comparison_id=f"bench_{dimension.replace(' ', '_')}",
            companies=companies,
            dimension=dimension,
            company_scores=scores_dict,
            winner=winner,
            gap_analysis=gaps,
            insights=insights
        )
    
    def create_full_benchmark(
        self,
        companies: List[str],
        dimensions: List[str],
        company_scores: Dict[str, Dict[str, PerceptionScore]]
    ) -> Dict[str, Any]:
        """Create comprehensive benchmark report"""
        logger.info(f"Creating full benchmark for {len(companies)} companies")
        
        benchmarks = []
        for dimension in dimensions:
            dim_scores = {}
            for company in companies:
                if company in company_scores and dimension in company_scores[company]:
                    dim_scores[company] = company_scores[company][dimension]
            
            if dim_scores:
                benchmark = self.create_dimension_benchmark(dimension, dim_scores)
                benchmarks.append(benchmark)
        
        # Create overall rankings
        overall_scores = self._calculate_overall_scores(company_scores, dimensions)
        
        # Generate strategic insights
        strategic_insights = self._generate_strategic_insights(
            companies, benchmarks, overall_scores
        )
        
        return {
            'benchmarks': [b.dict() for b in benchmarks],
            'overall_rankings': overall_scores,
            'strategic_insights': strategic_insights
        }
    
    def _calculate_gaps(self, scores_dict: Dict[str, float], leader: str) -> Dict[str, float]:
        """Calculate performance gaps vs leader"""
        leader_score = scores_dict[leader]
        gaps = {}
        
        for company, score in scores_dict.items():
            gaps[company] = leader_score - score
        
        return gaps
    
    def _generate_dimension_insights(
        self,
        dimension: str,
        company_scores: Dict[str, PerceptionScore]
    ) -> List[str]:
        """Generate insights for a dimension"""
        insights = []
        
        scores = sorted(
            company_scores.items(),
            key=lambda x: x[1].score,
            reverse=True
        )
        
        if len(scores) >= 2:
            leader = scores[0]
            second = scores[1]
            
            gap = leader[1].score - second[1].score
            
            if gap > 2:
                insights.append(
                    f"{leader[0]} has a clear advantage in {dimension} "
                    f"(gap: {gap:.1f} points)"
                )
            
            # Check if anyone is weak
            for company, score in scores:
                if score.score < 4:
                    insights.append(
                        f"{company} is weak in {dimension} "
                        f"({score.score:.1f}/10) - opportunity for improvement"
                    )
        
        return insights
    
    def _calculate_overall_scores(
        self,
        company_scores: Dict[str, Dict[str, PerceptionScore]],
        dimensions: List[str]
    ) -> Dict[str, float]:
        """Calculate overall scores across all dimensions"""
        overall = {}
        
        for company, dim_scores in company_scores.items():
            scores = [
                score.score
                for dim in dimensions
                if dim in dim_scores
                for score in [dim_scores[dim]]
            ]
            
            if scores:
                overall[company] = sum(scores) / len(scores)
            else:
                overall[company] = 5.0
        
        return overall
    
    def _generate_strategic_insights(
        self,
        companies: List[str],
        benchmarks: List[BenchmarkComparison],
        overall_scores: Dict[str, float]
    ) -> List[InsightFindings]:
        """Generate strategic insights from benchmarks"""
        insights = []
        
        # 1. Market leadership insights
        leader = max(overall_scores, key=overall_scores.get)
        insights.append(InsightFindings(
            insight_id="market_leader",
            category="competitive_position",
            title=f"{leader} is the overall market leader",
            description=f"{leader} leads across most dimensions with score {overall_scores[leader]:.1f}/10",
            companies_involved=[leader],
            evidence=[f"Overall score: {overall_scores[leader]:.1f}/10"],
            priority="high",
            impact_score=8.5
        ))
        
        # 2. Differentiation opportunities
        for benchmark in benchmarks:
            if benchmark.gap_analysis:
                laggards = [
                    company for company, gap in benchmark.gap_analysis.items()
                    if gap > 2
                ]
                if laggards and benchmark.company_scores:
                    leader_in_dim = max(benchmark.company_scores, key=benchmark.company_scores.get)
                    
                    insights.append(InsightFindings(
                        insight_id=f"opportunity_{benchmark.dimension}",
                        category="differentiation_opportunity",
                        title=f"Opportunity in {benchmark.dimension}",
                        description=f"{', '.join(laggards)} could improve {benchmark.dimension} positioning. "
                                   f"{leader_in_dim} leads with {benchmark.company_scores[leader_in_dim]:.1f}/10",
                        companies_involved=laggards,
                        evidence=benchmark.insights,
                        priority="medium",
                        impact_score=6.0
                    ))
        
        return insights


class PositioningComparison:
    """Compare brand positioning across companies"""
    
    def __init__(self, analyzer: RAGAnalyzer):
        self.analyzer = analyzer
    
    def compare_positioning(
        self,
        companies: List[str],
        brand_profiles: Dict[str, BrandPositioning]
    ) -> Dict[str, Any]:
        """Compare brand positioning across companies"""
        logger.info(f"Comparing positioning for {len(companies)} companies")
        
        comparison = {
            'companies': companies,
            'positioning_matrix': {},
            'differentiation_analysis': {},
            'messaging_comparison': {}
        }
        
        # Build positioning matrix
        attributes = ['trust_signals', 'emotional_themes', 'product_focus', 'target_segments']
        
        for attr in attributes:
            comparison['positioning_matrix'][attr] = {}
            for company in companies:
                if company in brand_profiles:
                    comparison['positioning_matrix'][attr][company] = \
                        getattr(brand_profiles[company], attr, [])
        
        # Analyze differentiation
        comparison['differentiation_analysis'] = self._analyze_differentiation(
            companies, brand_profiles
        )
        
        return comparison
    
    def _analyze_differentiation(
        self,
        companies: List[str],
        brand_profiles: Dict[str, BrandPositioning]
    ) -> Dict[str, Any]:
        """Analyze how companies differentiate"""
        analysis = {}
        
        for company in companies:
            if company in brand_profiles:
                profile = brand_profiles[company]
                
                analysis[company] = {
                    'unique_claims': profile.main_claims,
                    'emotional_focus': profile.emotional_themes,
                    'target_focus': profile.target_segments,
                    'product_emphasis': profile.product_focus
                }
        
        return analysis


__all__ = ["BenchmarkEngine", "PositioningComparison"]
