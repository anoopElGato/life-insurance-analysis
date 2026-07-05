# PDF Collector - Usage Examples

## Overview

The PDF Collector now supports **both remote URLs and local files**. This allows you to:
- Download and process PDFs from company websites
- Process local PDF files stored on your machine
- Mix both sources for the same company

---

## Basic Usage

### Example 1: URLs Only (Original)

```python
from src.collectors.pdf_collector import PDFCollector

# Create collector for HDFC Life
collector = PDFCollector(
    company="HDFC Life",
    pdf_urls=[
        "https://example.com/annual-report-2023.pdf",
        "https://example.com/brochure.pdf"
    ]
)

# Collect documents
documents = collector.collect()
```

### Example 2: Local Files Only (NEW!)

```python
from src.collectors.pdf_collector import PDFCollector

# Create collector
collector = PDFCollector(company="LIC")

# Add local PDF files
collector.add_pdf_file("/path/to/annual_report_2023.pdf")
collector.add_pdf_file("/path/to/brochure.pdf")

# Or add multiple at once
pdf_files = [
    "/data/lic/annual_report_2023.pdf",
    "/data/lic/product_guide.pdf",
    "/data/lic/financial_statements.pdf"
]
results = collector.add_pdf_files(pdf_files)

# Check which files were successfully added
for file_path, success in results.items():
    if success:
        print(f"✓ Added: {file_path}")
    else:
        print(f"✗ Failed: {file_path}")

# Collect documents
documents = collector.collect()
```

### Example 3: Mix URLs and Local Files (NEW!)

```python
from src.collectors.pdf_collector import PDFCollector

# Create collector
collector = PDFCollector(company="ICICI Prudential Life")

# Add URLs
collector.add_pdf_url("https://example.com/annual_report.pdf")
collector.add_pdf_url("https://example.com/brochure.pdf")

# Also add local files
collector.add_pdf_file("/data/icici/local_press_release.pdf")
collector.add_pdf_file("/data/icici/local_market_analysis.pdf")

# Collect from both sources
documents = collector.collect()
```

---

## Advanced Usage

### Check File Existence Before Adding

```python
from pathlib import Path
from src.collectors.pdf_collector import PDFCollector

collector = PDFCollector(company="SBI Life")

# Manually check before adding
local_files = [
    "/data/sbi/report1.pdf",
    "/data/sbi/report2.pdf"
]

for file_path in local_files:
    if Path(file_path).exists():
        collector.add_pdf_file(file_path)
        print(f"✓ {file_path}")
    else:
        print(f"✗ File not found: {file_path}")

documents = collector.collect()
```

### Use with Orchestrator

```python
from src.collectors.orchestrator import CollectionOrchestrator
from src.collectors.pdf_collector import PDFCollector

# Create orchestrator
orchestrator = CollectionOrchestrator()

# Setup PDF sources for each company
pdf_sources = {
    "HDFC Life": {
        "urls": [
            "https://hdfclife.com/files/annual-report-2023.pdf"
        ],
        "files": [
            "/local/data/hdfc/market_analysis.pdf"
        ]
    },
    "LIC": {
        "urls": [],
        "files": [
            "/local/data/lic/annual_report_2023.pdf",
            "/local/data/lic/brochure.pdf",
            "/local/data/lic/financial_statements.pdf"
        ]
    }
}

# Setup collectors
for company, sources in pdf_sources.items():
    collector = PDFCollector(company, pdf_urls=sources["urls"])
    
    # Add local files
    for file_path in sources["files"]:
        collector.add_pdf_file(file_path)
    
    # Register with orchestrator
    orchestrator.collectors[f"{company}_pdf"] = collector

# Collect all
documents = orchestrator.collect_all()
```

### Directory Scanning (NEW!)

```python
from pathlib import Path
from src.collectors.pdf_collector import PDFCollector

collector = PDFCollector(company="HDFC Life")

# Find all PDFs in a directory
pdf_directory = Path("/data/hdfc_pdfs")
pdf_files = list(pdf_directory.glob("*.pdf"))

# Add all found PDFs
results = collector.add_pdf_files([str(f) for f in pdf_files])

# Report
added = sum(1 for v in results.values() if v)
print(f"Added {added}/{len(pdf_files)} PDF files")

# Collect
documents = collector.collect()
```

---

## Complete Integration Example

```python
from pathlib import Path
from src.collectors.orchestrator import CollectionOrchestrator
from src.collectors.pdf_collector import PDFCollector

def setup_pdf_collection():
    """Setup comprehensive PDF collection"""
    
    orchestrator = CollectionOrchestrator()
    
    # Configuration
    companies_config = {
        "HDFC Life": {
            "local_dir": "/data/pdfs/hdfc",
            "urls": [
                "https://hdfclife.com/investor/reports/annual-report-2023.pdf",
                "https://hdfclife.com/products/brochure.pdf"
            ]
        },
        "LIC": {
            "local_dir": "/data/pdfs/lic",
            "urls": [
                "https://licindia.in/investor-relations/annual-reports.pdf"
            ]
        },
        "ICICI Prudential Life": {
            "local_dir": "/data/pdfs/icici",
            "urls": []
        }
    }
    
    # Setup collectors
    for company, config in companies_config.items():
        collector = PDFCollector(company, pdf_urls=config.get("urls", []))
        
        # Add local files from directory
        local_dir = Path(config["local_dir"])
        if local_dir.exists():
            pdf_files = list(local_dir.glob("*.pdf"))
            
            for pdf_file in pdf_files:
                if collector.add_pdf_file(str(pdf_file)):
                    print(f"✓ {company}: {pdf_file.name}")
                else:
                    print(f"✗ {company}: Failed to add {pdf_file.name}")
        
        # Register
        orchestrator.collectors[f"{company}_pdf"] = collector
    
    return orchestrator

# Run
orchestrator = setup_pdf_collection()
documents = orchestrator.collect_all()

print(f"\nTotal documents collected: {len(documents)}")
```

---

## Method Reference

### Initialize with URLs

```python
collector = PDFCollector(
    company="HDFC Life",
    pdf_urls=["https://example.com/report.pdf"]
)
```

### Add Single URL

```python
collector.add_pdf_url("https://example.com/report.pdf")
```

### Add Multiple URLs

```python
collector.add_pdf_urls([
    "https://example.com/report1.pdf",
    "https://example.com/report2.pdf"
])
```

### Add Single Local File

```python
success = collector.add_pdf_file("/path/to/local.pdf")
if success:
    print("File added successfully")
```

### Add Multiple Local Files

```python
results = collector.add_pdf_files([
    "/path/to/file1.pdf",
    "/path/to/file2.pdf"
])

for file_path, success in results.items():
    print(f"{file_path}: {'✓' if success else '✗'}")
```

### Collect All Documents

```python
documents = collector.collect()
```

---

## File Path Formats

### Local Files (Windows)

```python
collector.add_pdf_file(r"C:\Users\Data\HDFC\annual_report.pdf")
collector.add_pdf_file("C:/Users/Data/HDFC/annual_report.pdf")
collector.add_pdf_file("/c/Users/Data/HDFC/annual_report.pdf")  # WSL format
```

### Local Files (Mac/Linux)

```python
collector.add_pdf_file("/home/user/data/hdfc/annual_report.pdf")
collector.add_pdf_file("/Volumes/Data/hdfc/annual_report.pdf")
```

### Relative Paths

```python
collector.add_pdf_file("./data/pdfs/report.pdf")
collector.add_pdf_file("../data/hdfc/report.pdf")
```

### Using Path Objects

```python
from pathlib import Path

file_path = Path("/data/pdfs/report.pdf")
collector.add_pdf_file(str(file_path))
```

---

## Error Handling

### Check Before Adding

```python
from pathlib import Path

file_path = "/path/to/file.pdf"

if not Path(file_path).exists():
    print(f"File not found: {file_path}")
elif not Path(file_path).suffix.lower() == ".pdf":
    print(f"Not a PDF file: {file_path}")
else:
    collector.add_pdf_file(file_path)
```

### Check Results

```python
results = collector.add_pdf_files(file_list)

failed = [f for f, success in results.items() if not success]
if failed:
    print(f"Failed to add {len(failed)} files:")
    for f in failed:
        print(f"  - {f}")
```

---

## Metadata

Both local files and URLs store metadata:

```python
documents = collector.collect()

for doc in documents:
    print(f"Source: {doc.metadata['source_type']}")  # "local_file" or "url"
    print(f"URL: {doc.source_url}")
    print(f"Name: {doc.document_name}")
```

---

## Tips & Best Practices

### 1. Organize Files by Company

```
/data/pdfs/
├── hdfc/
│   ├── annual_report_2023.pdf
│   ├── annual_report_2022.pdf
│   └── brochure.pdf
├── lic/
│   ├── annual_report_2023.pdf
│   └── financial_statements.pdf
└── icici/
    ├── annual_report_2023.pdf
    └── investor_guide.pdf
```

### 2. Batch Processing with Orchestrator

```python
# Setup all collectors at once
for company in ["HDFC Life", "LIC", "ICICI Prudential Life"]:
    collector = PDFCollector(company)
    
    # Add files from standard directory
    local_dir = Path(f"/data/pdfs/{company.lower()}")
    pdf_files = list(local_dir.glob("*.pdf"))
    
    collector.add_pdf_files([str(f) for f in pdf_files])
    orchestrator.collectors[f"{company}_pdf"] = collector
```

### 3. Mix with Web Collector

```python
# Use WebCollector for discovery, PDFCollector for detailed PDFs
web_collector = WebCollector("HDFC Life")
pdf_collector = PDFCollector("HDFC Life")

# Add specific PDFs directly
pdf_collector.add_pdf_files([
    "/data/hdfc_detailed_analysis_1.pdf",
    "/data/hdfc_detailed_analysis_2.pdf"
])

# Combine collectors
orchestrator.collectors["web"] = web_collector
orchestrator.collectors["pdf"] = pdf_collector
```

### 4. Logging

```python
import logging
from src.utils.logger import get_logger

logger = get_logger("pdf_setup")

collector = PDFCollector("HDFC Life")
results = collector.add_pdf_files(file_list)

for file_path, success in results.items():
    if success:
        logger.info(f"Added PDF: {file_path}")
    else:
        logger.error(f"Failed to add PDF: {file_path}")
```

---

## Summary

**New Capabilities:**
- ✅ Add local PDF files by path
- ✅ Mix URLs and local files
- ✅ Batch add multiple files
- ✅ Validate file existence
- ✅ Track source type (local vs URL)
- ✅ Error handling for missing/invalid files

**Backward Compatible:**
- ✅ Existing URL-only code still works
- ✅ No breaking changes

**Use Cases:**
- Upload company PDFs directly
- Process downloaded documents
- Mix online and offline sources
- Systematic batch processing
