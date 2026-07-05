"""
Report generation engine
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import json
import csv
from src.utils.logger import get_logger
from src.utils.models import (
    BrandPositioning, PerceptionScore, CompanyProfile, BenchmarkComparison,
    CustomerReviewSentiment, InsightFindings, Report
)
from config.settings import OUTPUT_DIR

logger = get_logger("reporting.engine")


class ReportGenerator:
    """Generate comprehensive reports in multiple formats"""
    
    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or OUTPUT_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_brand_profile_report(
        self,
        company: str,
        positioning: BrandPositioning,
        perception_scores: Dict[str, PerceptionScore],
        review_sentiment: Optional[CustomerReviewSentiment] = None
    ) -> Report:
        """Generate brand profile report"""
        logger.info(f"Generating brand profile report for {company}")
        
        report = Report(
            report_type="brand_profile",
            title=f"Brand Profile Report: {company}",
            companies_included=[company],
            analysis_summary={
                'company': company,
                'positioning_statement': positioning.positioning_statement,
                'total_claims': len(positioning.main_claims),
                'key_differentiators': positioning.key_differentiators,
                'target_segments': positioning.target_segments,
                'perception_scores': {
                    dim: score.score
                    for dim, score in perception_scores.items()
                }
            },
            detailed_findings=[
                {
                    'type': 'positioning',
                    'content': positioning.dict()
                },
                {
                    'type': 'perception_scores',
                    'content': {
                        dim: score.dict()
                        for dim, score in perception_scores.items()
                    }
                }
            ]
        )
        
        if review_sentiment:
            report.detailed_findings.append({
                'type': 'customer_sentiment',
                'content': review_sentiment.dict()
            })
        
        return report
    
    def generate_benchmark_report(
        self,
        companies: List[str],
        benchmarks: List[BenchmarkComparison],
        insights: List[InsightFindings]
    ) -> Report:
        """Generate competitive benchmark report"""
        logger.info(f"Generating benchmark report for {len(companies)} companies")
        
        report = Report(
            report_type="benchmark",
            title=f"Competitive Benchmark Report: {', '.join(companies)}",
            companies_included=companies,
            analysis_summary={
                'total_companies': len(companies),
                'dimensions_analyzed': len(benchmarks),
                'benchmark_dimensions': [b.dimension for b in benchmarks]
            },
            detailed_findings=[
                {
                    'type': 'benchmark',
                    'content': b.dict()
                }
                for b in benchmarks
            ],
            recommendations=self._generate_recommendations(benchmarks, insights)
        )
        
        return report
    
    def generate_executive_summary(
        self,
        companies: List[str],
        company_profiles: Dict[str, CompanyProfile],
        benchmarks: List[BenchmarkComparison],
        insights: List[InsightFindings]
    ) -> Report:
        """Generate executive summary report"""
        logger.info(f"Generating executive summary for {len(companies)} companies")
        
        report = Report(
            report_type="executive_summary",
            title=f"Executive Summary: Life Insurance Brand Analysis",
            companies_included=companies,
            analysis_summary=self._build_executive_summary(
                companies, company_profiles, benchmarks
            ),
            recommendations=self._generate_strategic_recommendations(insights)
        )
        
        return report
    
    def save_report_json(self, report: Report, filename: Optional[str] = None) -> Path:
        """Save report as JSON"""
        if filename is None:
            filename = f"{report.report_type}_{report.report_id}.json"
        
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report.dict(), f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"Saved JSON report to {filepath}")
        return filepath
    
    def save_report_markdown(self, report: Report, filename: Optional[str] = None) -> Path:
        """Save report as Markdown"""
        if filename is None:
            filename = f"{report.report_type}_{report.report_id}.md"
        
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# {report.title}\n\n")
            f.write(f"**Generated:** {report.generated_at.isoformat()}\n")
            f.write(f"**Companies:** {', '.join(report.companies_included)}\n\n")
            
            # Summary
            f.write("## Executive Summary\n")
            for key, value in report.analysis_summary.items():
                f.write(f"- **{key}:** {value}\n")
            f.write("\n")
            
            # Detailed Findings
            if report.detailed_findings:
                f.write("## Detailed Findings\n")
                for finding in report.detailed_findings:
                    f.write(f"### {finding.get('type', 'Finding')}\n")
                    f.write(f"```json\n{json.dumps(finding.get('content', {}), indent=2)}\n```\n\n")
            
            # Recommendations
            if report.recommendations:
                f.write("## Recommendations\n")
                for i, rec in enumerate(report.recommendations, 1):
                    f.write(f"{i}. {rec}\n")
        
        logger.info(f"Saved Markdown report to {filepath}")
        return filepath
    
    def save_report_csv(
        self,
        data: List[Dict[str, Any]],
        filename: str
    ) -> Path:
        """Save data as CSV"""
        filepath = self.output_dir / filename
        
        if not data:
            logger.warning("No data to save")
            return filepath
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        
        logger.info(f"Saved CSV report to {filepath}")
        return filepath
    
    def _build_executive_summary(
        self,
        companies: List[str],
        company_profiles: Dict[str, CompanyProfile],
        benchmarks: List[BenchmarkComparison]
    ) -> Dict[str, Any]:
        """Build executive summary data"""
        summary = {
            'market_overview': {
                'companies_analyzed': len(companies),
                'total_documents': sum(
                    cp.total_documents_analyzed
                    for cp in company_profiles.values()
                ),
                'analysis_date': datetime.now().isoformat()
            },
            'key_findings': [],
            'competitive_positions': {}
        }
        
        # Add key findings
        for benchmark in benchmarks:
            if benchmark.winner:
                summary['key_findings'].append(
                    f"{benchmark.winner} leads in {benchmark.dimension}"
                )
        
        # Add competitive positions
        for company in companies:
            if company in company_profiles:
                profile = company_profiles[company]
                summary['competitive_positions'][company] = {
                    'positioning': profile.positioning.positioning_statement,
                    'key_strengths': profile.positioning.key_differentiators[:3],
                    'avg_perception_score': sum(profile.perception_scores.values()) / len(profile.perception_scores) if profile.perception_scores else 0
                }
        
        return summary
    
    def _generate_recommendations(
        self,
        benchmarks: List[BenchmarkComparison],
        insights: List[InsightFindings]
    ) -> List[str]:
        """Generate strategic recommendations"""
        recommendations = []
        
        for insight in insights:
            if insight.priority == "high":
                recommendations.append(f"HIGH PRIORITY: {insight.title}")
            elif insight.recommendations:
                recommendations.extend(insight.recommendations)
        
        return recommendations[:10]  # Limit to 10
    
    def _generate_strategic_recommendations(self, insights: List[InsightFindings]) -> List[str]:
        """Generate executive-level recommendations"""
        recommendations = []
        
        for insight in sorted(insights, key=lambda x: x.impact_score, reverse=True):
            if len(recommendations) < 5:
                recommendations.append(
                    f"• {insight.title}: {insight.description}"
                )
        
        return recommendations


__all__ = ["ReportGenerator"]
