# Insurance Brand Analytics Platform

> **âœ¨ NEW: Completely FREE with Local LLMs! No API costs required.**
> 
> Uses free Ollama models instead of paid cloud APIs. See [LOCAL_LLM_SETUP.md](LOCAL_LLM_SETUP.md) for details.

A comprehensive AI-powered system for analyzing consumer perception of life insurance brands in India.

## Overview

This platform automatically:

1. **Collects** data from company websites, reports, and public sources
2. **Processes** text and creates semantic embeddings
3. **Analyzes** brand positioning and messaging using LLM
4. **Discovers** perception dimensions automatically
5. **Scores** companies on perception factors
6. **Benchmarks** competitors across dimensions
7. **Generates** strategic insights and reports
8. **Visualizes** findings in an interactive dashboard

## Features

### Data Collection
- Web scraping of company websites
- PDF document ingestion (annual reports, brochures)
- Automatic text extraction and cleaning
- Duplicate detection and deduplication

### Text Processing
- Intelligent document chunking
- Metadata extraction and tagging
- Content deduplication
- Quality validation

### AI-Powered Analysis
- RAG (Retrieval-Augmented Generation) system
- LLM-based brand positioning extraction
- Automatic perception dimension discovery
- Evidence-based perception scoring
- Customer sentiment analysis

### Competitive Intelligence
- Dimension-based benchmarking
- Positioning comparison matrix
- Gap analysis
- Strategic insight generation

### Reporting
- Multi-format exports (JSON, CSV, Markdown)
- Brand profile reports
- Competitive benchmark reports
- Executive summaries
- Interactive Streamlit dashboard

## System Architecture

```
DATA COLLECTION LAYER
â”œâ”€ Web Collector (websites)
â”œâ”€ PDF Collector (reports, brochures)
â”œâ”€ Social Media Collector (future)
â””â”€ Review Collector (future)
        â†“
TEXT PROCESSING LAYER
â”œâ”€ Text Cleaning
â”œâ”€ Chunking & Deduplication
â””â”€ Metadata Enrichment
        â†“
VECTOR EMBEDDING LAYER
â”œâ”€ Embedding Generation (FREE: sentence-transformers)
â””â”€ ChromaDB Storage (FREE: local)
        â†“
RAG RETRIEVAL LAYER
â”œâ”€ Semantic Search
â”œâ”€ Relevance Filtering
â””â”€ Context Compilation
        â†“
LLM ANALYSIS LAYER
â”œâ”€ FREE Local LLM (Ollama: Mistral, Neural-Chat, etc.)
â”œâ”€ Brand Positioning Extraction
â”œâ”€ Perception Dimension Scoring
â”œâ”€ Insight Generation
â””â”€ Sentiment Analysis
        â†“
BENCHMARKING LAYER
â”œâ”€ Dimension Comparison
â”œâ”€ Gap Analysis
â””â”€ Competitive Insights
        â†“
REPORTING & VISUALIZATION
â”œâ”€ Report Generation
â”œâ”€ Dashboard
â””â”€ Data Exports
```

## Installation

### Prerequisites
- Python 3.10+
- Ollama (FREE, download from https://ollama.ai)
- 4GB RAM minimum (8GB recommended)
- 10GB disk space (for models and data)
- **No API keys needed - completely free!**

### Setup

1. **Clone/Extract the project**
   ```bash
   cd insurance_analytics
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # Windows
   # or
   source venv/bin/activate      # Mac/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   # Copy example configuration
   cp .env.example .env
   
   # (Optional) Edit .env to customize model or settings
   # Defaults are already set for local FREE LLM:
   # LOCAL_LLM_MODEL=mistral (free, fast, good quality)
   # LOCAL_EMBEDDING_MODEL=all-MiniLM-L6-v2 (free, local)
   ```

5. **Install Ollama (FREE LLM) - Required**
   - Download from https://ollama.ai
   - Pull a model: `ollama pull mistral`
   - Keep Ollama running in background

6. **Initialize the system**
   ```bash
   python initialize.py
   ```

## Usage

### Running the Complete Pipeline

```bash
python main.py
```

This executes all 8 pipeline stages:
1. Data Collection
2. Text Processing  
3. Embeddings & Vector DB
4. RAG System Initialization
5. Brand Intelligence Extraction
6. Perception Dimension Analysis
7. Competitor Benchmarking
8. Report Generation

### Running the Dashboard

```bash
streamlit run src/dashboard/app.py
```

Access at: `http://localhost:8501`

### Running Individual Examples

```bash
# See detailed usage examples
python examples/pipeline_example.py
```

## Project Structure

```
insurance_analytics/
â”œâ”€â”€ config/
â”‚   â””â”€â”€ settings.py                 # Configuration management
â”œâ”€â”€ src/
â”‚   â”œâ”€â”€ collectors/                 # Data collection modules
â”‚   â”‚   â”œâ”€â”€ base.py                # Abstract collector
â”‚   â”‚   â”œâ”€â”€ web_collector.py       # Website scraping
â”‚   â”‚   â”œâ”€â”€ pdf_collector.py       # PDF ingestion
â”‚   â”‚   â””â”€â”€ orchestrator.py        # Collection orchestrator
â”‚   â”œâ”€â”€ processors/                 # Text processing
â”‚   â”‚   â””â”€â”€ text_processor.py       # Chunking & deduplication
â”‚   â”œâ”€â”€ embeddings/                 # Vector embeddings
â”‚   â”‚   â””â”€â”€ vector_db.py           # ChromaDB management
â”‚   â”œâ”€â”€ rag/                        # RAG system
â”‚   â”‚   â”œâ”€â”€ retriever.py           # Document retrieval
â”‚   â”‚   â””â”€â”€ analyzer.py            # LLM analysis
â”‚   â”œâ”€â”€ analysis/                   # Analysis engines
â”‚   â”‚   â”œâ”€â”€ dimensions.py          # Perception dimensions
â”‚   â”‚   â””â”€â”€ reviews.py             # Sentiment analysis
â”‚   â”œâ”€â”€ benchmarking/               # Benchmarking
â”‚   â”‚   â””â”€â”€ engine.py              # Benchmark generation
â”‚   â”œâ”€â”€ reporting/                  # Report generation
â”‚   â”‚   â””â”€â”€ engine.py              # Multi-format reporting
â”‚   â”œâ”€â”€ dashboard/                  # Visualization
â”‚   â”‚   â””â”€â”€ app.py                 # Streamlit dashboard
â”‚   â””â”€â”€ utils/                      # Utilities
â”‚       â”œâ”€â”€ logger.py              # Logging
â”‚       â”œâ”€â”€ models.py              # Data models
â”‚       â””â”€â”€ helpers.py             # Helper functions
â”œâ”€â”€ data/
â”‚   â”œâ”€â”€ raw/                        # Raw collected documents
â”‚   â”œâ”€â”€ processed/                  # Processed chunks
â”‚   â”œâ”€â”€ embeddings/                 # ChromaDB storage
â”‚   â””â”€â”€ outputs/                    # Generated reports
â”œâ”€â”€ logs/
â”‚   â””â”€â”€ app.log                     # Application logs
â”œâ”€â”€ tests/                          # Test suite
â”œâ”€â”€ examples/                       # Usage examples
â”œâ”€â”€ main.py                         # Pipeline entry point
â”œâ”€â”€ initialize.py                   # System initialization
â””â”€â”€ requirements.txt                # Python dependencies
```

## Configuration

### Companies
```python
COMPANIES = {
    "HDFC Life": {...},
    "LIC": {...},
    "ICICI Prudential Life": {...},
    "SBI Life": {...}
}
```

### Data Sources
- **Website**: Company main website and product pages
- **Annual Reports**: PDF documents from investor relations
- **Brochures**: Product and service brochures
- **Press Releases**: News and announcements
- **Customer Reviews**: Public feedback and ratings

### Perception Dimensions
The system automatically discovers 8+ dimensions including:
- Trust & Reliability
- Innovation
- Customer Service
- Digital Experience
- Affordability
- Security & Protection
- Transparency
- Brand Legacy

## API Reference

### CollectionOrchestrator

```python
from src.collectors.orchestrator import CollectionOrchestrator

orchestrator = CollectionOrchestrator()
orchestrator.setup_default_collectors()
documents = orchestrator.collect_all()
```

### TextProcessor

```python
from src.processors.text_processor import TextProcessor

processor = TextProcessor()
chunks = processor.process_documents(documents)
processor.save_processed_chunks()
```

### VectorDatabase

```python
from src.embeddings.vector_db import VectorDatabase

vector_db = VectorDatabase()
vector_db.create_collection("brand_documents")
vector_db.add_chunks("brand_documents", chunks)
results = vector_db.search("brand positioning", top_k=5)
```

### RAGAnalyzer

```python
from src.rag.analyzer import RAGAnalyzer

analyzer = RAGAnalyzer(retriever)
positioning = analyzer.analyze_brand_positioning("HDFC Life")
scores = analyzer.score_perception_dimension("HDFC Life", "Trust", "...")
```

### ReportGenerator

```python
from src.reporting.engine import ReportGenerator

generator = ReportGenerator()
report = generator.generate_brand_profile_report(...)
generator.save_report_json(report)
generator.save_report_markdown(report)
```

## Output Examples

### Brand Profile Report
```json
{
  "company": "HDFC Life",
  "positioning_statement": "...",
  "main_claims": [...],
  "trust_signals": [...],
  "perception_scores": {
    "Trust": 8.5,
    "Innovation": 8.1,
    ...
  }
}
```

### Benchmark Report
```json
{
  "dimension": "Trust & Reliability",
  "companies": ["HDFC Life", "LIC", "ICICI Prudential", "SBI Life"],
  "scores": {"HDFC Life": 8.5, "LIC": 8.2, ...},
  "winner": "HDFC Life",
  "insights": [...]
}
```

## Customization

### Adding New Companies

Edit `config/settings.py`:
```python
COMPANIES = {
    "New Company": {
        "full_name": "Company Full Name",
        "website": "https://...",
        "founded": 2020
    }
}
```

### Adding New Data Sources

Create a new collector in `src/collectors/`:
```python
from src.collectors.base import BaseCollector

class SocialMediaCollector(BaseCollector):
    def collect(self):
        # Implementation
        pass
```

### Customizing Perception Dimensions

Edit `config/settings.py`:
```python
BENCHMARK_METRICS = [
    "dimension1",
    "dimension2",
    ...
]
```

## Performance Considerations

- **Data Collection**: 5-15 minutes per company
- **Embedding Creation**: 2-5 minutes (depends on chunk count)
- **LLM Analysis**: 3-10 minutes (depends on document volume)
- **Report Generation**: <1 minute

### Optimization Tips
- Use batch processing for large datasets
- Cache embeddings and avoid re-embedding
- Set appropriate chunk sizes (default: 500 tokens)
- Use top_k=3-5 for faster RAG retrieval

## Troubleshooting

### "Ollama connection refused"
```bash
ollama serve
```

### ChromaDB Connection Issues
```bash
# Reinitialize database
rm -rf data/embeddings
python initialize.py
```

### Out of Memory
- Reduce `EMBEDDING_BATCH_SIZE` in config
- Process companies separately
- Reduce chunk overlap

## Contributing

1. Create feature branch
2. Make changes
3. Add tests
4. Submit pull request

## License

Proprietary - HDFC Life Corporate Internship Project

## Support

For issues and questions:
- Check `logs/app.log` for error details
- Review the examples in `examples/` directory
- Refer to API documentation in code docstrings

## Future Enhancements

- [ ] Social media sentiment analysis
- [ ] Real-time data collection
- [ ] Multi-language support
- [ ] Advanced NLP models
- [ ] Competitor tracking dashboard
- [ ] Automated insight generation
- [ ] Email reporting
- [ ] API server deployment

---

**Version**: 1.0.0  
**Last Updated**: 2024  
**Author**: HDFC Life Analytics Team


