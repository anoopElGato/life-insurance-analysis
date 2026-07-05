# Architecture Documentation

## System Design Overview

The Insurance Brand Analytics Platform is built using a modular, layered architecture that separates concerns and enables independent scaling of each component.

## Layers

### 1. Data Collection Layer (`src/collectors/`)

**Purpose**: Extract data from multiple sources

**Components**:
- `BaseCollector`: Abstract base class defining collector interface
- `WebCollector`: Web scraping using requests + BeautifulSoup
- `PDFCollector`: PDF ingestion using pdfplumber
- `CollectionOrchestrator`: Coordinates collection from all sources

**Data Flow**:
```
[Companies] â†’ [Collectors] â†’ [Raw Documents] â†’ [Storage (JSONL)]
```

**Features**:
- Multi-source data gathering
- Duplicate URL detection
- Domain validation
- Error handling with retry logic
- Batch processing

### 2. Text Processing Layer (`src/processors/`)

**Purpose**: Clean, chunk, and structure raw text

**Components**:
- `TextProcessor`: Main text processing pipeline

**Processing Steps**:
1. Text cleaning (whitespace normalization, special char removal)
2. Smart chunking (sentence-aware, with overlap)
3. Deduplication (similarity-based)
4. Metadata enrichment

**Data Structure**:
```python
ProcessedChunk {
    id,
    document_id,
    company,
    source_type,
    chunk_index,
    text,
    chunk_size,
    metadata,
    processed_at
}
```

**Configuration**:
- `EMBEDDING_CHUNK_SIZE`: 500 tokens
- `EMBEDDING_OVERLAP`: 50 tokens
- Deduplication threshold: 0.9 (90% similarity)

### 3. Embeddings & Vector Database Layer (`src/embeddings/`)

**Purpose**: Create semantic embeddings and enable similarity search

**Components**:
- `EmbeddingManager`: Handles local sentence-transformer embedding generation
- `VectorDatabase`: ChromaDB wrapper for storage and retrieval

**Architecture**:
```
[Text Chunks] â†’ [Local Embeddings] â†’ [ChromaDB] â†’ [Vector Index]
                                                      â†“
                                                  [Search]
```

**Features**:
- Batch embedding generation
- Metadata storage
- Similarity search
- Collection-based organization
- Persistence

**Database Schema**:
```
Collection: brand_documents
â”œâ”€â”€ id: string (unique)
â”œâ”€â”€ embedding: vector[384] (all-MiniLM-L6-v2 by default)
â”œâ”€â”€ document: string (original text)
â””â”€â”€ metadata:
    â”œâ”€â”€ company: string
    â”œâ”€â”€ source_type: enum
    â”œâ”€â”€ document_name: string
    â”œâ”€â”€ chunk_index: int
    â””â”€â”€ [source-specific fields]
```

### 4. RAG System Layer (`src/rag/`)

**Purpose**: Retrieve relevant context and augment LLM analysis

**Components**:
- `DocumentRetriever`: Semantic search over embeddings
- `RAGAnalyzer`: LLM-based analysis with retrieved context

**Retrieval Pipeline**:
```
[Query] â†’ [Embedding] â†’ [Similarity Search] â†’ [Relevance Filtering] â†’ [Context Compilation]
```

**Retrieval Configuration**:
- `RAG_TOP_K`: 5 documents
- `RAG_RELEVANCE_THRESHOLD`: 0.5 (cosine similarity)

**LLM Integration**:
- Model: Local Ollama model (mistral by default)
- Temperature: 0.7 (analysis), 0.5 (scoring)
- System prompts for domain-specific tasks

### 5. Analysis Layer (`src/analysis/`)

**Purpose**: Extract insights and score perceptions

**Components**:
- `DimensionDiscovery`: Automatically discover perception dimensions
- `PerceptionScorer`: Score companies on dimensions
- `ReviewAnalyzer`: Sentiment and topic analysis

**Process**:
```
[Raw Documents] â†’ [Theme Extraction] â†’ [Dimension Generation] â†’ [Structured Framework]
                                             â†“
                                    [Dimension Definitions] â†’ [Scoring]
```

**Dimension Discovery**:
1. Sample documents from each company
2. Extract recurring themes with LLM
3. Convert themes to structured dimensions
4. Create scoring criteria

**Scoring Methodology**:
- Evidence-based (only cite found facts)
- Multi-document consensus
- Confidence scoring
- Supporting snippets

### 6. Benchmarking Layer (`src/benchmarking/`)

**Purpose**: Compare companies and generate competitive insights

**Components**:
- `BenchmarkEngine`: Create dimension benchmarks
- `PositioningComparison`: Compare positioning strategies

**Analysis**:
```
[Perception Scores] â†’ [Gap Analysis] â†’ [Competitive Positioning] â†’ [Strategic Insights]
```

**Benchmark Outputs**:
- Dimension-level scores for all companies
- Performance gaps vs. leader
- Winner identification
- Comparative insights

### 7. Reporting Layer (`src/reporting/`)

**Purpose**: Generate multi-format reports

**Components**:
- `ReportGenerator`: Create different report types

**Report Types**:
1. **Brand Profile Reports**
   - Positioning statement
   - Claims and trust signals
   - Perception scores
   - Customer sentiment

2. **Benchmark Reports**
   - Dimension comparisons
   - Performance gaps
   - Winner identification
   - Competitive insights

3. **Executive Summaries**
   - Key findings
   - Overall rankings
   - Strategic recommendations

**Output Formats**:
- JSON (structured data)
- Markdown (human-readable)
- CSV (data tables)

### 8. Dashboard Layer (`src/dashboard/`)

**Purpose**: Interactive visualization and exploration

**Components**:
- Streamlit-based web interface

**Sections**:
- Dashboard overview
- Individual brand profiles
- Competitor benchmarks
- Review analysis
- Data management

## Data Flow

### End-to-End Pipeline

```
START
  â†“
[1. DATA COLLECTION]
  - Web scraping
  - PDF ingestion
  â†“
[2. TEXT PROCESSING]
  - Cleaning
  - Chunking
  - Deduplication
  â†“
[3. EMBEDDINGS]
  - local sentence-transformer generation
  - ChromaDB storage
  â†“
[4. RAG INITIALIZATION]
  - Retriever setup
  - Analyzer initialization
  â†“
[5. BRAND EXTRACTION]
  - Positioning analysis
  - Claims extraction
  - Trust signal identification
  â†“
[6. PERCEPTION ANALYSIS]
  - Dimension discovery
  - Company scoring
  - Review analysis
  â†“
[7. BENCHMARKING]
  - Dimension comparison
  - Gap analysis
  - Insight generation
  â†“
[8. REPORTING]
  - Report generation
  - Multi-format export
  - Dashboard updates
  â†“
END
```

## Configuration Management

### Settings Hierarchy

```
Environment Variables (.env)
    â†“
config/settings.py
    â”œâ”€ API Configuration
    â”œâ”€ Database Configuration
    â”œâ”€ Company Configuration
    â”œâ”€ Data Source Configuration
    â”œâ”€ Processing Configuration
    â””â”€ Analysis Configuration
```

### Key Configurations

**Companies**:
```python
COMPANIES = {
    "Company Name": {
        "website": "...",
        "founded": YYYY
    }
}
```

**Data Sources**:
```python
DATA_SOURCES = {
    "source_name": {
        "enabled": bool,
        "priority": int,
        "description": str
    }
}
```

**Perception Metrics**:
```python
BENCHMARK_METRICS = ["metric1", "metric2", ...]
```

## Error Handling & Resilience

### Collection Layer
- Retry logic with exponential backoff
- Request timeout handling
- Connection failure recovery
- Validation before storage

### Processing Layer
- Chunk validation
- Metadata consistency checks
- Error logging and continuation

### Analysis Layer
- LLM response parsing with fallbacks
- Confidence scoring for validation
- Evidence requirement enforcement

### Database Layer
- Connection retry
- Data persistence verification
- Collection integrity checks

## Scalability Considerations

### Horizontal Scaling
- Independent data collectors
- Batch processing support
- Parallel company analysis

### Vertical Scaling
- Configurable batch sizes
- Chunk size optimization
- Memory-efficient streaming

### Performance Optimization
- Caching mechanisms
- Batch embeddings
- Indexed search
- Lazy loading

## Security Considerations

### Local Model Configuration
- Environment variable storage for local model settings
- No hardcoding of model host or model name
- Model switching via `.env`

### Data Privacy
- Local data storage
- No external data leakage
- Audit logging

### Access Control
- Future: API key authentication
- Future: Role-based access

## Extensibility

### Adding New Companies
1. Add to `COMPANIES` in config
2. Run collection orchestrator

### Adding New Data Sources
1. Create collector class inheriting `BaseCollector`
2. Implement `collect()` method
3. Register in orchestrator

### Adding New Perception Dimensions
1. Dimension discovery will auto-discover
2. Or manually define in configuration

### Adding New Analysis Types
1. Create analyzer class in `src/analysis/`
2. Implement analysis logic
3. Update pipeline

## Technology Stack

### Data Collection
- **Requests**: HTTP client
- **BeautifulSoup**: HTML parsing
- **Playwright**: Browser automation (future)
- **pdfplumber**: PDF extraction

### Processing
- **Pandas**: Data manipulation
- **NLTK/SpaCy**: NLP (future)

### Embeddings & Storage
- **sentence-transformers**: Local embedding models
- **ChromaDB**: Vector database
- **Ollama HTTP API**: LLM framework

### Analysis & LLM
- **Ollama HTTP API**: Framework
- **Ollama**: Local LLM engine

### Visualization
- **Streamlit**: Dashboard
- **Plotly**: Charts
- **Pandas**: Data display

### Infrastructure
- **Python 3.10+**: Runtime
- **Logging**: Built-in + structured
- **JSON/CSV**: Data formats

---

For implementation details, refer to individual module documentation in source code.



