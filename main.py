"""
Main pipeline orchestrator
"""

from typing import Dict, List, Optional
from pathlib import Path
import json
from datetime import datetime

from src.utils.logger import get_logger
from src.collectors.orchestrator import CollectionOrchestrator
from src.processors.text_processor import TextProcessor
from src.embeddings.vector_db import VectorDatabase
from src.rag.retriever import DocumentRetriever
from src.rag.analyzer import RAGAnalyzer
from src.analysis.dimensions import DimensionDiscovery, PerceptionScorer
from src.analysis.reviews import ReviewAnalyzer
from src.benchmarking.engine import BenchmarkEngine, PositioningComparison
from src.reporting.engine import ReportGenerator
from src.utils.models import PerceptionDimension, BrandPositioning
from config.settings import COMPANIES, BENCHMARK_METRICS

logger = get_logger("pipeline.orchestrator")


class AnalyticsPipeline:
    """Complete analytics pipeline orchestrator"""
    
    def __init__(self):
        logger.info("Initializing Analytics Pipeline")
        
        # Initialize components
        self.collection_orchestrator = CollectionOrchestrator()
        self.text_processor = TextProcessor()
        self.vector_db = VectorDatabase()
        self.retriever = None
        self.analyzer = None
        self.dimension_discovery = None
        self.perception_scorer = None
        self.benchmark_engine = None
        self.positioning_comparison = None
        self.report_generator = ReportGenerator()
        self.review_analyzer = ReviewAnalyzer()
        
        # Results storage
        self.documents = {}
        self.processed_chunks = []
        self.brand_profiles = {}
        self.perception_scores = {}
        self.benchmarks = []
        self.insights = []
    
    def run_full_pipeline(self) -> Dict[str, any]:
        """Run the complete pipeline from data collection to reporting"""
        logger.info("=" * 80)
        logger.info("STARTING INSURANCE BRAND ANALYTICS PIPELINE")
        logger.info("=" * 80)
        
        try:
            # Step 1: Data Collection
            logger.info("\n[STEP 1/8] DATA COLLECTION")
            self._collect_data()
            
            # Step 2: Text Processing
            logger.info("\n[STEP 2/8] TEXT PROCESSING")
            self._process_text()
            
            # Step 3: Embeddings and Vector DB
            logger.info("\n[STEP 3/8] EMBEDDINGS & VECTOR DATABASE")
            self._create_embeddings()
            
            # Step 4: Initialize RAG components
            logger.info("\n[STEP 4/8] RAG SYSTEM INITIALIZATION")
            self._initialize_rag()
            
            # Step 5: Brand Intelligence Extraction
            logger.info("\n[STEP 5/8] BRAND INTELLIGENCE EXTRACTION")
            self._extract_brand_profiles()
            
            # Step 6: Perception Dimension Analysis
            logger.info("\n[STEP 6/8] PERCEPTION DIMENSION ANALYSIS")
            self._analyze_perceptions()
            
            # Step 7: Competitor Benchmarking
            logger.info("\n[STEP 7/8] COMPETITOR BENCHMARKING")
            self._benchmark_competitors()
            
            # Step 8: Report Generation
            logger.info("\n[STEP 8/8] REPORT GENERATION")
            self._generate_reports()
            
            logger.info("\n" + "=" * 80)
            logger.info("PIPELINE EXECUTION COMPLETED SUCCESSFULLY")
            logger.info("=" * 80)
            
            return self._compile_results()
        
        except Exception as e:
            logger.error(f"Pipeline execution failed: {str(e)}", exc_info=True)
            raise
    
    def _collect_data(self) -> None:
        """Step 1: Collect data from all sources"""
        logger.info("Collecting data from company sources...")
        
        self.collection_orchestrator.setup_default_collectors()
        self.documents = self.collection_orchestrator.collect_all()
        self.collection_orchestrator.save_raw_documents()
        
        stats = self.collection_orchestrator.get_collection_stats()
        logger.info(f"Collection Statistics: {json.dumps(stats, indent=2)}")
    
    def _process_text(self) -> None:
        """Step 2: Process and chunk text"""
        logger.info("Processing and chunking text documents...")
        
        all_documents = self.collection_orchestrator.get_all_documents()
        self.processed_chunks = self.text_processor.process_documents(all_documents)
        self.text_processor.save_processed_chunks()
        
        stats = self.text_processor.get_chunks_stats()
        logger.info(f"Processing Statistics: {json.dumps(stats, indent=2)}")
    
    def _create_embeddings(self) -> None:
        """Step 3: Create embeddings and build vector database"""
        logger.info("Creating embeddings and populating vector database...")
        
        # Create main collection
        self.vector_db.create_collection("brand_documents")
        
        # Add chunks to database
        self.vector_db.add_chunks("brand_documents", self.processed_chunks)
        
        # Get stats
        stats = self.vector_db.get_collection_stats("brand_documents")
        logger.info(f"Vector DB Statistics: {json.dumps(stats, indent=2)}")
        
        # Persist
        self.vector_db.persist()
    
    def _initialize_rag(self) -> None:
        """Step 4: Initialize RAG components"""
        logger.info("Initializing Retrieval-Augmented Generation components...")
        
        self.retriever = DocumentRetriever(self.vector_db, "brand_documents")
        self.analyzer = RAGAnalyzer(self.retriever)
        
        logger.info("RAG components initialized successfully")
    
    def _extract_brand_profiles(self) -> None:
        """Step 5: Extract brand positioning and profiles"""
        logger.info("Extracting brand positioning and creating profiles...")
        
        for company in COMPANIES.keys():
            logger.info(f"Analyzing {company}...")
            
            try:
                # Get brand positioning
                positioning = self.analyzer.analyze_brand_positioning(company)
                self.brand_profiles[company] = positioning
                
                logger.info(f"✓ {company} profile extracted")
                logger.debug(f"Positioning: {positioning.positioning_statement}")
            
            except Exception as e:
                logger.error(f"Error extracting profile for {company}: {str(e)}")
    
    def _analyze_perceptions(self) -> None:
        """Step 6: Discover dimensions and score perceptions"""
        logger.info("Analyzing perception dimensions...")
        
        # Initialize dimension discovery
        self.dimension_discovery = DimensionDiscovery(self.vector_db)
        
        # Discover dimensions
        companies = list(COMPANIES.keys())
        perception_dimensions = self.dimension_discovery.discover_dimensions(companies)
        
        logger.info(f"Discovered {len(perception_dimensions)} perception dimensions:")
        for dim in perception_dimensions:
            logger.info(f"  - {dim.dimension_name}: {dim.description}")
        
        # Score all companies on all dimensions
        self.perception_scorer = PerceptionScorer(self.retriever)
        
        for company in companies:
            logger.info(f"Scoring {company} on perception dimensions...")
            self.perception_scores[company] = {}
            
            for dimension in perception_dimensions:
                try:
                    score = self.perception_scorer._score_company_dimension(company, dimension)
                    self.perception_scores[company][dimension.dimension_name] = score
                    
                    logger.debug(f"  {dimension.dimension_name}: {score.score:.1f}/10")
                
                except Exception as e:
                    logger.error(f"Error scoring {company} on {dimension.dimension_name}: {str(e)}")
    
    def _benchmark_competitors(self) -> None:
        """Step 7: Create benchmarks and competitive analysis"""
        logger.info("Creating competitive benchmarks...")
        
        self.benchmark_engine = BenchmarkEngine(self.analyzer, self.retriever)
        self.positioning_comparison = PositioningComparison(self.analyzer)
        
        companies = list(COMPANIES.keys())
        
        # Create benchmarks
        for metric in BENCHMARK_METRICS:
            try:
                company_scores = {
                    company: self.perception_scores.get(company, {}).get(metric)
                    for company in companies
                }
                
                company_scores = {
                    k: v for k, v in company_scores.items() if v is not None
                }
                
                if company_scores:
                    benchmark = self.benchmark_engine.create_dimension_benchmark(metric, company_scores)
                    self.benchmarks.append(benchmark)
            
            except Exception as e:
                logger.warning(f"Error creating benchmark for {metric}: {str(e)}")
        
        logger.info(f"Created {len(self.benchmarks)} benchmark comparisons")
    
    def _generate_reports(self) -> None:
        """Step 8: Generate reports"""
        logger.info("Generating analysis reports...")
        
        try:
            # Generate brand profile reports
            for company, positioning in self.brand_profiles.items():
                perception_scores = self.perception_scores.get(company, {})
                
                report = self.report_generator.generate_brand_profile_report(
                    company,
                    positioning,
                    perception_scores
                )
                
                # Save in multiple formats
                self.report_generator.save_report_json(report)
                self.report_generator.save_report_markdown(report)
                
                logger.info(f"Generated report for {company}")
            
            # Generate benchmark report
            companies = list(COMPANIES.keys())
            insights = self.benchmark_engine._generate_strategic_insights(
                companies, self.benchmarks, {}
            )
            self.insights = insights
            
            benchmark_report = self.report_generator.generate_benchmark_report(
                companies,
                self.benchmarks,
                insights
            )
            
            self.report_generator.save_report_json(benchmark_report)
            self.report_generator.save_report_markdown(benchmark_report)
            
            logger.info("Generated benchmark report")
            
            # Generate executive summary
            company_profiles = {
                company: positioning
                for company, positioning in self.brand_profiles.items()
            }
            
            executive_report = self.report_generator.generate_executive_summary(
                companies,
                {},  # Simplified for now
                self.benchmarks,
                insights
            )
            
            self.report_generator.save_report_json(executive_report)
            self.report_generator.save_report_markdown(executive_report)
            
            logger.info("Generated executive summary")
        
        except Exception as e:
            logger.error(f"Error generating reports: {str(e)}")
    
    def _compile_results(self) -> Dict[str, any]:
        """Compile all results"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'companies_analyzed': len(COMPANIES),
            'documents_processed': len(self.processed_chunks),
            'brand_profiles': len(self.brand_profiles),
            'perception_dimensions': len(set().union(*[
                set(scores.keys()) for scores in self.perception_scores.values()
            ])),
            'benchmarks': len(self.benchmarks),
            'insights': len(self.insights),
            'reports_generated': True
        }
        
        return results


def main():
    """Main entry point"""
    pipeline = AnalyticsPipeline()
    results = pipeline.run_full_pipeline()
    
    print("\n" + "=" * 80)
    print("PIPELINE RESULTS SUMMARY")
    print("=" * 80)
    print(json.dumps(results, indent=2))
    print("=" * 80)


if __name__ == "__main__":
    main()
