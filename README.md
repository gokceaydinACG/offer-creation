# 📊 Offer Creation Tool

AI-powered system for standardizing heterogeneous supplier offers (Excel, PDF, Images) into consistent Excel formats for food and HPC (Health & Personal Care) categories.

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat&logo=python&logoColor=white)](https://python.org)
[![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=flat&logo=openai&logoColor=white)](https://openai.com)

---

## 🎯 Overview

The Offer Creation Tool transforms diverse supplier offer formats into standardized, professional Excel outputs. It combines AI-powered data extraction with intelligent field mapping and validation to ensure consistency across all offers.

### Key Features

✅ **Multi-Format Support**
- Excel files (.xlsx, .xls)
- PDF documents (.pdf)
- Images/Screenshots (.jpg, .png, .jpeg)

✅ **AI-Powered Extraction**
- GPT-4 for intelligent data extraction
- Multilingual support (FR, ES, DE, NL, IT)
- Automatic field mapping and normalization

✅ **Smart Processing**
- Packaging math calculations (pieces ↔ cases ↔ pallets)
- Content extraction and normalization
- Product description cleaning and translation
- Double-stackable pallet calculations

✅ **Professional Output**
- Standardized Excel format with formatting
- Article number generation (AC00001000+)
- Product image integration
- Consistent data structure

---

## 📁 Project Structure

```
offer_creation/
├── article_number/       # Article number generation logic
├── config/              # Configuration and settings
├── domain/              # Data schemas and canonical models
│   ├── canonical.py     # Canonical data structure
│   └── schemas/         # FOOD and HPC output schemas
├── extraction/          # AI extraction layer
│   ├── chunked_processor.py  # LLM chunking for large files
│   ├── llm_client.py         # OpenAI API client
│   ├── prompts.py            # System prompts
│   └── to_canonical.py       # Excel/PDF/Image → Canonical
├── fields/              # Field-specific logic
│   ├── normalization.py      # Content/language normalization
│   └── packaging_math.py     # Packaging calculations
├── input_readers/       # File format readers
│   ├── excel.py         # Excel reader
│   ├── image.py         # Image to base64 converter
│   └── pdf.py           # PDF reader
├── interface/           # Streamlit UI
│   ├── app.py          # Main application
│   ├── components.py   # UI components
│   ├── processor.py    # File processing orchestrator
│   └── styles.py       # CSS styling
├── mapping/            # Canonical → Category mapping
│   ├── to_food.py      # FOOD category mapper
│   └── to_hpc.py       # HPC category mapper
├── runners/            # Processing pipelines
│   └── pipeline.py     # Main processing pipeline
└── writers/            # Output generation
    └── excel_writer.py # Excel file writer with images
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- OpenAI API key
- Git

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/amsterdam-consumer-goods/offer-creation.git
cd offer-creation
```

2. **Create virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set environment variables**

Create a `.env` file:
```bash
OPENAI_API_KEY=sk-proj-your-api-key-here
MAX_FILE_SIZE_MB=20
MAX_SHEET_ROWS=1000
MAX_SHEET_COLS=50
MAX_SHEETS=10
```

5. **Run the application**
```bash
streamlit run interface/app.py
```

The app will open at `http://localhost:8501`

---

## 📖 Usage Guide

### Basic Workflow

1. **Select Department**
   - Choose FOOD or HPC category
   - Enable "Double Stackable" for double-height pallets
   - Enable "With Price" to extract pricing data

2. **Upload Offer File**
   - Drag and drop or browse
   - Supported: Excel, PDF, Images
   - Max size: 20MB per file

3. **Process Offer**
   - Click "Process Offer"
   - AI extracts and standardizes data
   - Review results in data table

4. **Add Product Images** (Optional)
   - Upload images for specific products
   - Images appear in final Excel

5. **Download Excel**
   - Download with or without images
   - Professional formatted output
   - Ready for distribution

### Supported Input Formats

#### Excel Files
- **Formats:** .xlsx, .xls
- **Requirements:** Row 1 = headers, Row 2+ = data
- **Validation:** Automatic sheet/row/column limits
- **Best for:** Structured supplier offers

#### PDF Files
- **Formats:** .pdf
- **Extraction:** Text-based extraction
- **Best for:** Digital supplier catalogs

#### Images
- **Formats:** .jpg, .png, .jpeg
- **Extraction:** GPT-4 Vision OCR
- **Best for:** Screenshots, photos of offers

---

## 🏗️ Architecture

### Processing Pipeline

```
┌─────────────────┐
│  File Upload    │
│  (Excel/PDF/IMG)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ File Validation │
│  (Size/Format)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Input Reader   │
│ excel/pdf/image │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ AI Extraction   │
│   (GPT-4/4o)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Canonical      │
│  (Standardized) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Normalization   │
│ + Packaging Math│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Category Mapping│
│  (FOOD or HPC)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Article Numbers │
│   AC00001000+   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Excel Output   │
│  (Formatted)    │
└─────────────────┘
```

### Data Flow

**Raw Input** → **Canonical Format** → **Category Schema** → **Excel Output**

#### Canonical Format
Intermediate format used across all input types:
- `ean`: EAN unit code
- `product_description`: ENGLISH, ALL CAPS
- `content`: 500GR, 1L, etc.
- `languages`: EN/DE/FR
- `piece_per_case`: Units per case
- `case_per_pallet`: Cases per pallet
- `pieces_per_pallet`: Total pieces per pallet
- `bbd`: Best before date (FOOD only)
- `availability_pieces`: Available pieces
- `availability_cartons`: Available cases
- `availability_pallets`: Available pallets
- `price_unit_eur`: Unit price in EUR

---

## ⚙️ Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | Required | OpenAI API key for GPT-4 |
| `MAX_FILE_SIZE_MB` | 20 | Maximum file size |
| `MAX_SHEET_ROWS` | 1000 | Max rows per Excel sheet |
| `MAX_SHEET_COLS` | 50 | Max columns per sheet |
| `MAX_SHEETS` | 10 | Max sheets per workbook |
| `EXTREME_COLS_LIMIT` | 100 | Hard limit for columns |

### Customization

#### Adding New Categories

1. Create schema in `domain/schemas/`
2. Add mapper in `mapping/`
3. Update `runners/pipeline.py`

#### Modifying Extraction Prompts

Edit `extraction/prompts.py`:
- `EXTRACTION_SYSTEM_PROMPT`: Core extraction rules
- `build_extraction_prompt()`: Dynamic prompt builder
- `get_image_extraction_prompt()`: Image-specific prompt

---

## 🌐 Deployment

### Streamlit Cloud

1. **Push to GitHub**
```bash
git add .
git commit -m "Update configuration"
git push origin main
```

2. **Deploy on Streamlit Cloud**
   - Visit https://share.streamlit.io
   - Click "New app"
   - Select repository: `amsterdam-consumer-goods/offer-creation`
   - Branch: `main`
   - Main file: `interface/app.py`

3. **Add Secrets**

Go to App Settings → Secrets:
```toml
OPENAI_API_KEY = "sk-proj-..."
```

4. **Deploy**
   - Click "Deploy"
   - Wait 2-3 minutes
   - App will be live at `https://your-app.streamlit.app`

### Docker (Alternative)

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8501

CMD ["streamlit", "run", "interface/app.py"]
```

```bash
docker build -t offer-creation .
docker run -p 8501:8501 -e OPENAI_API_KEY=sk-... offer-creation
```

---

## 🔧 Troubleshooting

### Common Issues

#### "File is too large"
- **Cause:** Excel file exceeds row/column limits
- **Solution:** Filter data or split file
- **Limits:** 1000 rows, 50 columns per sheet

#### "AI returned invalid data format"
- **Cause:** LLM returned malformed JSON
- **Solution:** Retry with cleaner data or smaller file
- **Prevention:** Use structured Excel with clear headers

#### "Vision API failed"
- **Cause:** Image quality too low or API error
- **Solution:** Use higher quality image or check API key
- **Tip:** Works best with clear table structures

#### "Price extraction not working"
- **Cause:** "With Price" checkbox not enabled
- **Solution:** Enable checkbox before processing
- **Note:** Price field is optional

### Debug Mode

Enable detailed logging:
```python
# Add to config/settings.py
DEBUG = True
LOG_LEVEL = "DEBUG"
```

### Logs

View Streamlit Cloud logs:
- Go to app dashboard
- Click "Manage app"
- View "Logs" tab

---

## 📊 Output Specifications

### FOOD Category Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| Article Number | String | AC + 8 digits | AC00001234 |
| EAN code unit | String | Unit EAN | 8719200000000 |
| Product Description | String | ENGLISH, ALL CAPS | OREO ORIGINAL 154GR |
| Content | String | Net content | 154GR |
| Languages | String | ISO codes | EN/FR/DE |
| Piece per case | Integer | Units per case | 24 |
| Case per pallet | Integer | Cases per pallet | 216 |
| Pieces per pallet | Integer | Total pieces | 5184 |
| BBD | String | Best before | 180 DAYS |
| Availability/Pieces | Integer | Available units | 10000 |
| Availability/Cartons | Integer | Available cases | 416 |
| Availability/Pallets | Integer | Available pallets | 2 |
| Price/unit (Euro) | Float | Unit price | 0.85 |

### HPC Category Fields

Same as FOOD, but **without BBD** (best before date).

---

## 🧪 Testing

### Manual Testing

Test each input type:
```bash
# Excel
python -m pytest tests/test_excel_extraction.py

# PDF
python -m pytest tests/test_pdf_extraction.py

# Images
python -m pytest tests/test_image_extraction.py
```

### Test Files

Example test files in `tests/fixtures/`:
- `sample_offer.xlsx`
- `sample_offer.pdf`
- `sample_offer.jpg`

---

## 🤝 Contributing

### Development Workflow

1. **Create feature branch**
```bash
git checkout -b feature/your-feature-name
```

2. **Make changes**
   - Follow PEP 8 style guide
   - Add docstrings to functions
   - Update tests if needed

3. **Test locally**
```bash
streamlit run interface/app.py
```

4. **Commit and push**
```bash
git add .
git commit -m "Add: your feature description"
git push origin feature/your-feature-name
```

5. **Create Pull Request**
   - Go to GitHub repository
   - Click "New Pull Request"
   - Describe changes
   - Request review

### Code Style

- **Formatting:** Black (line length 100)
- **Imports:** isort
- **Type hints:** Use where appropriate
- **Docstrings:** Google style

---

## 📝 License

Copyright © 2024 Amsterdam Consumer Goods

This software is proprietary and confidential.

---

## 🙋 Support

### Internal Support

- **Email:** gaydin@amsterdamconsumergoods.com
- **Slack:** #offer-creation-tool

### Documentation

- [Specification Document](./Offer_Creation___Excel_Output_Specification_V1_food__Hpc_en.pdf)
- [API Documentation](./docs/API.md)
- [Architecture Guide](./docs/ARCHITECTURE.md)

---

## 🗺️ Roadmap

### Current Version: v1.0
- ✅ Multi-format input (Excel, PDF, Images)
- ✅ AI-powered extraction
- ✅ FOOD and HPC categories
- ✅ Product image integration
- ✅ Streamlit Cloud deployment

### Planned Features: v1.1
- 🔄 Batch processing (multiple files)
- 🔄 Custom field mapping
- 🔄 Export to CSV
- 🔄 Advanced filtering

### Future: v2.0
- 📅 API endpoint for integrations
- 📅 User management and permissions
- 📅 Historical offer tracking
- 📅 Analytics dashboard

---

## 📌 Version History

### v1.0.0 (Current)
- Initial release
- Multi-format support
- AI extraction with GPT-4
- Professional Excel output
- Streamlit Cloud deployment
