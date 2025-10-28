# PRIIPS Document Extraction & RAG Workflow

Complete workflow for extracting PRIIPS KID documents and querying with LLM context.

## 📁 Directory Structure

```
priips_documents/
├── raw/           # Place your PDF documents here
├── extracted/     # Extracted JSON documents (auto-generated)
└── processed/     # Chunked documents for RAG (future)

scripts/
├── extract_priips.py      # Extract text from PDFs
└── query_with_context.py  # Query LLM with document context
```

## 🚀 Quick Start

### 1. Add PRIIPS Documents

Place PDF documents in `priips_documents/raw/`:

```bash
# Naming convention: {ISIN}_{ProductName}_{Date}.pdf
cp /path/to/your/priips.pdf priips_documents/raw/LU1234567890_GlobalEquity_2024.pdf
```

### 2. Extract Document Content

```bash
# Extract all PDFs in the raw directory
python scripts/extract_priips.py priips_documents/raw/

# Or extract a single file
python scripts/extract_priips.py priips_documents/raw/LU1234567890_GlobalEquity_2024.pdf
```

**Output:** JSON files in `priips_documents/extracted/` with structured content:
- Metadata (ISIN, product name, dates)
- Raw extracted text
- Parsed sections (objectives, risks, costs, etc.)

### 3. Query with RAG Context

```bash
# Ask questions about your documents
python scripts/query_with_context.py "What is the recommended holding period?"

python scripts/query_with_context.py "What are the main risks of this investment?"

python scripts/query_with_context.py "Summarize the cost structure"
```

**Options:**
```bash
# Specify different extracted directory
python scripts/query_with_context.py "Your question" --extracted-dir custom/path/

# Control context size and response length
python scripts/query_with_context.py "Your question" \
  --max-context 3000 \
  --max-tokens 800
```

## 📊 Example Workflow

```bash
# 1. Add a PRIIPS PDF
cp MyFund.pdf priips_documents/raw/FR0012345678_MyFund_2024.pdf

# 2. Extract content
python scripts/extract_priips.py priips_documents/raw/

# Output:
# 📄 Processing: FR0012345678_MyFund_2024.pdf
# ✅ Extracted 12,543 characters
# 💾 Saved to: priips_documents/extracted/FR0012345678_MyFund_2024_extracted.json

# 3. Query the LLM
python scripts/query_with_context.py "What is the SRI of this fund?"

# Output:
# 📚 Loading documents from priips_documents/extracted...
# ✅ Loaded 1 documents
# 🔍 Querying LLM with 1,234 chars of context...
# 📊 Tokens used: 234
#
# 💬 Answer:
# Based on the PRIIPS document, the Summary Risk Indicator (SRI) for this fund is 5 out of 7...
```

## 🎯 Use Cases

### Document Comparison
```bash
python scripts/query_with_context.py "Compare the risk profiles of all available funds"
```

### Specific Information Extraction
```bash
python scripts/query_with_context.py "Extract all recommended holding periods"
python scripts/query_with_context.py "List all ISINs and their product names"
```

### Compliance Checks
```bash
python scripts/query_with_context.py "Are there any funds with SRI above 6?"
python scripts/query_with_context.py "Which funds have holding periods under 3 years?"
```

## 🔧 Advanced: Integrate with PydanticAI

```python
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel

# Configure with your deployed service
model = OpenAIModel(
    'DragonLLM/qwen3-8b-fin-v1.0',
    base_url='https://jeanbaptdzd-priips-llm-service.hf.space/v1',
)

agent = Agent(model=model)

# Load PRIIPS context
with open('priips_documents/extracted/LU123_extracted.json') as f:
    context = json.load(f)

# Query with context
result = agent.run_sync(
    f"Based on this PRIIPS document: {context['raw_text'][:2000]}... "
    f"What is the recommended holding period?"
)
```

## 📝 Extracted Document Schema

```json
{
  "metadata": {
    "filename": "LU1234567890_GlobalEquity_2024.pdf",
    "extraction_date": "2024-10-28T16:24:00",
    "isin": "LU1234567890",
    "product_name": "GlobalEquity",
    "file_size_bytes": 245678,
    "text_length": 12543
  },
  "raw_text": "Full extracted text from PDF...",
  "sections": {
    "summary": "What is this product? ...",
    "objectives": "Investment objectives and policy...",
    "risk_indicator": "SRI: 5/7 ...",
    "performance_scenarios": "Performance scenarios...",
    "costs": "What are the costs? ...",
    "holding_period": "Recommended: 5 years"
  }
}
```

## 🚀 Next Steps

1. **Add More Documents:** Place additional PRIIPS PDFs in `raw/`
2. **Enhance Extraction:** Improve section parsing in `extract_priips.py`
3. **Add Embeddings:** Implement vector search for better RAG
4. **Build API:** Create REST API endpoints for document queries
5. **Dashboard:** Build web UI for document management and queries

## 📚 API Integration

The LLM service is OpenAI-compatible and deployed at:
```
https://jeanbaptdzd-priips-llm-service.hf.space/v1
```

**Endpoints:**
- `GET /` - Service status
- `GET /v1/models` - List available models
- `POST /v1/chat/completions` - Chat completion with context

See `test_service.py` for integration examples.

