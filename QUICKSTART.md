# Quick Start Guide - FREE LOCAL LLM VERSION

## âš¡ 5-Minute Setup (No API Keys Needed!)

### 1. Install Ollama (FREE Local LLM)

**Windows/Mac**: Download from https://ollama.ai

**Linux**: `curl https://ollama.ai/install.sh | sh`

### 2. Pull a Model

```bash
# Fast & Good (Recommended)
ollama pull mistral

# Or choose: neural-chat (faster), dolphin-mixtral (better), llama2 (best)
```

### 3. Start Ollama

**Windows/Mac**: Ollama app runs in background automatically

**Linux**: `ollama serve` (keep running in separate terminal)

### 4. Install Python Dependencies

```bash
cd insurance_analytics
python -m venv venv
source venv/Scripts/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### 5. Configure (Optional)

```bash
cp .env.example .env
# Defaults work perfectly - no changes needed!
```

### 6. Initialize

```bash
python initialize.py
```

### 7. Run

```bash
# Full pipeline (15-40 min, depending on model)
python main.py

# Or just the dashboard
streamlit run src/dashboard/app.py
```

---

## âœ“ Cost Summary

| Component | Cost |
|-----------|------|
| Ollama LLM | FREE âœ“ |
| Embeddings | FREE âœ“ |
| ChromaDB | FREE âœ“ |
| Dashboard | FREE âœ“ |
| **Total** | **FREE** âœ“ |

**No API keys. No subscriptions. No costs.**

---

## What Happens During Pipeline

### Stage 1: Data Collection (2-5 min)
- Visits company websites
- Downloads PDFs
- Extracts text

**Stage 2: Text Processing (<1 min)**
- Cleans text
- Breaks into chunks
- Removes duplicates

**Stage 3: Embeddings (2-5 min)**
- Converts text to embeddings
- Stores in vector database

**Stage 4: RAG Setup (<1 min)**
- Initializes retrieval system
- Sets up LLM connection

**Stage 5: Brand Analysis (3-8 min)**
- Extracts positioning for each company
- Identifies main claims
- Finds trust signals

**Stage 6: Perception Scoring (5-10 min)**
- Discovers perception dimensions
- Scores each company
- Analyzes reviews

**Stage 7: Benchmarking (2-5 min)**
- Compares companies
- Identifies gaps
- Generates insights

**Stage 8: Reporting (<1 min)**
- Generates JSON reports
- Creates Markdown summaries
- Saves to `data/outputs/`

**Total Time**: ~15-40 minutes (depending on document volume)

## Output Files

After running the pipeline, check:

```
data/outputs/
â”œâ”€â”€ brand_profile_*.json          # Individual company analysis
â”œâ”€â”€ brand_profile_*.md            # Readable reports
â”œâ”€â”€ benchmark_*.json              # Benchmark data
â”œâ”€â”€ executive_summary_*.md        # Executive summary
â””â”€â”€ config.json                   # Configuration used
```

## Using Individual Components

### Just Collect Data

```python
from src.collectors.orchestrator import CollectionOrchestrator

orchestrator = CollectionOrchestrator()
orchestrator.setup_default_collectors()
documents = orchestrator.collect_all()
```

### Just Process Text

```python
from src.processors.text_processor import TextProcessor

processor = TextProcessor()
chunks = processor.process_documents(documents)
```

### Just Search

```python
from src.embeddings.vector_db import VectorDatabase
from src.rag.retriever import DocumentRetriever

vector_db = VectorDatabase()
retriever = DocumentRetriever(vector_db, "brand_documents")

results = retriever.retrieve("brand positioning", company="HDFC Life")
for result in results:
    print(result['text'])
```

### Just Analyze

```python
from src.rag.analyzer import RAGAnalyzer

analyzer = RAGAnalyzer(retriever)
positioning = analyzer.analyze_brand_positioning("HDFC Life")
print(positioning.positioning_statement)
```

## Dashboard

```bash
streamlit run src/dashboard/app.py
```

Opens at: `http://localhost:8501`

Features:
- Brand profile views
- Competitive benchmarks
- Sentiment analysis
- Data export

## Troubleshooting

### "ModuleNotFoundError"

```bash
# Make sure you're in the project directory
cd insurance_analytics

# And packages are installed
pip install -r requirements.txt
```

### "Ollama connection refused"

```bash
# Set in environment
ollama serve

# Or in .env file
echo "LOCAL_LLM_MODEL=mistral" >> .env
```

### "ChromaDB error"

```bash
# Reinitialize database
rm -rf data/embeddings
python initialize.py
```

### "Out of memory"

Edit `config/settings.py`:
```python
EMBEDDING_BATCH_SIZE = 10  # Reduce from 100
```

## What Data Is Analyzed?

- Company websites
- Annual reports
- Product brochures
- Press releases
- Public documents

**Privacy**: Only public information is collected

## Understanding Results

### Perception Scores (0-10)
- 0-2: No emphasis
- 3-4: Weak emphasis
- 5-6: Moderate emphasis
- 7-8: Strong emphasis
- 9-10: Very strong emphasis

### Benchmarks
Shows which company is strongest in each dimension:
- **Leader**: Highest score
- **Gap**: How far behind others are
- **Insights**: Why they're ahead/behind

### Reports
- **JSON**: For data analysis
- **Markdown**: For reading/presentations
- **Dashboard**: For visualization

## Next Steps

1. **Customize Companies**
   - Edit `config/settings.py`
   - Add your own insurance companies

2. **Add More Data**
   - Implement new collectors in `src/collectors/`
   - Add social media, reviews, etc.

3. **Extend Analysis**
   - Add custom perception dimensions
   - Implement new analysis types

4. **Deploy**
   - Host dashboard on cloud
   - Set up automated collection
   - Create API endpoints

## Key Files

| File | Purpose |
|------|---------|
| `main.py` | Run full pipeline |
| `initialize.py` | Setup system |
| `config/settings.py` | All configuration |
| `src/dashboard/app.py` | Web dashboard |
| `examples/pipeline_example.py` | Usage examples |
| `README.md` | Full documentation |
| `ARCHITECTURE.md` | Technical design |

## Need Help?

1. Check `logs/app.log` for errors
2. Review `examples/pipeline_example.py` for patterns
3. Read docstrings in source code
4. Check `README.md` for detailed docs

---

Happy analyzing! ðŸ“Š

