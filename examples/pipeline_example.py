"""
Example script demonstrating complete pipeline usage
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.collectors.orchestrator import CollectionOrchestrator
from src.processors.text_processor import TextProcessor
from src.embeddings.vector_db import VectorDatabase
from src.rag.retriever import DocumentRetriever
from src.rag.analyzer import RAGAnalyzer
from src.analysis.dimensions import DimensionDiscovery, PerceptionScorer
from src.benchmarking.engine import BenchmarkEngine
from src.reporting.engine import ReportGenerator
from src.utils.logger import get_logger
from config.settings import COMPANIES
import json

logger = get_logger("examples.pipeline")


def example_data_collection():
    """Example: Collecting data"""
    print("\n" + "=" * 80)
    print("EXAMPLE 1: DATA COLLECTION")
    print("=" * 80)
    
    # Create collection orchestrator
    orchestrator = CollectionOrchestrator()
    orchestrator.setup_default_collectors()
    
    # Collect from all sources
    collected_data = orchestrator.collect_all()
    
    # Print statistics
    for company, documents in collected_data.items():
        print(f"\n{company}:")
        print(f"  Documents collected: {len(documents)}")
        if documents:
            print(f"  First document: {documents[0].document_name}")
            print(f"  Source: {documents[0].source_url}")
    
    return orchestrator


def example_text_processing(orchestrator):
    """Example: Text processing"""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: TEXT PROCESSING")
    print("=" * 80)
    
    # Get all documents
    documents = orchestrator.get_all_documents()
    
    # Create processor
    processor = TextProcessor()
    
    # Process documents
    chunks = processor.process_documents(documents)
    
    # Print statistics
    stats = processor.get_chunks_stats()
    print(f"\nProcessing Statistics:")
    print(json.dumps(stats, indent=2))
    
    # Save processed chunks
    processor.save_processed_chunks()
    print(f"\nChunks saved to disk")
    
    return processor, chunks


def example_embeddings_and_rag(chunks):
    """Example: Embeddings and RAG"""
    print("\n" + "=" * 80)
    print("EXAMPLE 3: EMBEDDINGS & RAG")
    print("=" * 80)
    
    # Create vector database
    vector_db = VectorDatabase()
    
    # Create collection and add chunks
    vector_db.create_collection("brand_documents")
    vector_db.add_chunks("brand_documents", chunks)
    
    # Get collection stats
    stats = vector_db.get_collection_stats("brand_documents")
    print(f"\nVector Database Statistics:")
    print(json.dumps(stats, indent=2))
    
    # Create retriever
    retriever = DocumentRetriever(vector_db, "brand_documents")
    
    # Example retrieval
    print(f"\nExample Retrieval:")
    query = "What is HDFC Life's positioning on digital innovation?"
    results = retriever.retrieve(query, company="HDFC Life", top_k=3)
    
    print(f"\nQuery: {query}")
    print(f"Retrieved {len(results)} results:")
    for i, result in enumerate(results, 1):
        print(f"  {i}. {result['metadata']['document_name'][:50]}... (relevance: {result['relevance_score']:.1%})")
    
    return vector_db, retriever


def example_brand_analysis(retriever):
    """Example: Brand positioning analysis"""
    print("\n" + "=" * 80)
    print("EXAMPLE 4: BRAND POSITIONING ANALYSIS")
    print("=" * 80)
    
    analyzer = RAGAnalyzer(retriever)
    
    # Analyze HDFC Life
    company = "HDFC Life"
    print(f"\nAnalyzing {company}...")
    
    positioning = analyzer.analyze_brand_positioning(company)
    
    print(f"\nPositioning Analysis for {company}:")
    print(f"  Positioning: {positioning.positioning_statement}")
    print(f"  Main Claims: {', '.join(positioning.main_claims[:3])}")
    print(f"  Trust Signals: {', '.join(positioning.trust_signals[:3])}")
    print(f"  Emotional Themes: {', '.join(positioning.emotional_themes[:2])}")
    print(f"  Confidence: {positioning.confidence:.1%}")
    
    return analyzer


def example_perception_scoring(vector_db, retriever):
    """Example: Perception dimension discovery and scoring"""
    print("\n" + "=" * 80)
    print("EXAMPLE 5: PERCEPTION DIMENSION ANALYSIS")
    print("=" * 80)
    
    # Discover dimensions
    dimension_discovery = DimensionDiscovery(vector_db)
    companies = list(COMPANIES.keys())
    
    print(f"\nDiscovering perception dimensions for {len(companies)} companies...")
    dimensions = dimension_discovery.discover_dimensions(companies)
    
    print(f"\nDiscovered {len(dimensions)} perception dimensions:")
    for dim in dimensions[:5]:
        print(f"  • {dim.dimension_name}")
        print(f"    {dim.description}")
    
    # Score companies
    print(f"\nScoring companies on dimensions...")
    scorer = PerceptionScorer(retriever)
    
    company = "HDFC Life"
    dimension = dimensions[0]
    
    score = scorer._score_company_dimension(company, dimension)
    
    print(f"\n{company} on {dimension.dimension_name}:")
    print(f"  Score: {score.score:.1f}/10")
    print(f"  Rationale: {score.rationale}")
    print(f"  Confidence: {score.confidence:.1%}")
    
    return dimensions


def example_benchmarking(analyzer, retriever, dimensions):
    """Example: Competitor benchmarking"""
    print("\n" + "=" * 80)
    print("EXAMPLE 6: COMPETITOR BENCHMARKING")
    print("=" * 80)
    
    benchmark_engine = BenchmarkEngine(analyzer, retriever)
    
    companies = list(COMPANIES.keys())
    
    # Create benchmarks for first dimension
    if dimensions:
        dimension = dimensions[0]
        
        # Get scores for all companies on this dimension
        company_scores = {}
        for company in companies:
            scorer = PerceptionScorer(retriever)
            score = scorer._score_company_dimension(company, dimension)
            company_scores[company] = score
        
        # Create benchmark
        benchmark = benchmark_engine.create_dimension_benchmark(
            dimension.dimension_name,
            company_scores
        )
        
        print(f"\nBenchmark for {dimension.dimension_name}:")
        print(f"  Leader: {benchmark.winner}")
        
        print(f"\nScores:")
        for company, score in benchmark.company_scores.items():
            print(f"  {company}: {score:.1f}/10")
        
        print(f"\nInsights:")
        for insight in benchmark.insights[:3]:
            print(f"  • {insight}")


def example_reporting():
    """Example: Report generation"""
    print("\n" + "=" * 80)
    print("EXAMPLE 7: REPORT GENERATION")
    print("=" * 80)
    
    report_generator = ReportGenerator()
    
    print(f"\nReport generator initialized")
    print(f"Output directory: {report_generator.output_dir}")
    print(f"\nReport generator can create:")
    print(f"  • Brand Profile Reports (JSON, Markdown)")
    print(f"  • Competitor Benchmark Reports")
    print(f"  • Executive Summaries")
    print(f"  • CSV data exports")


def run_all_examples():
    """Run all examples"""
    print("\n")
    print("█" * 80)
    print("█" + " " * 78 + "█")
    print("█" + "INSURANCE BRAND ANALYTICS - USAGE EXAMPLES".center(78) + "█")
    print("█" + " " * 78 + "█")
    print("█" * 80)
    
    try:
        # Example 1: Data Collection
        orchestrator = example_data_collection()
        
        # Example 2: Text Processing
        processor, chunks = example_text_processing(orchestrator)
        
        # Example 3: Embeddings & RAG
        vector_db, retriever = example_embeddings_and_rag(chunks)
        
        # Example 4: Brand Analysis
        analyzer = example_brand_analysis(retriever)
        
        # Example 5: Perception Scoring
        dimensions = example_perception_scoring(vector_db, retriever)
        
        # Example 6: Benchmarking
        example_benchmarking(analyzer, retriever, dimensions)
        
        # Example 7: Reporting
        example_reporting()
        
        print("\n" + "=" * 80)
        print("ALL EXAMPLES COMPLETED SUCCESSFULLY")
        print("=" * 80)
    
    except Exception as e:
        logger.error(f"Error running examples: {str(e)}", exc_info=True)
        print(f"\nError: {str(e)}")


if __name__ == "__main__":
    run_all_examples()
