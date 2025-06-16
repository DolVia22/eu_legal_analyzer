# EU Legal Analyzer

A comprehensive AI-powered application that analyzes company profiles against EU legal acts to determine compliance requirements and relevance using Hugging Face models and web scraping from EUR-Lex.

## Features

- 🏢 **Company Profile Management**: Create detailed company profiles with industry, business activities, and compliance areas
- 🔍 **AI-Powered Legal Analysis**: Uses Hugging Face transformers to match legal acts with company profiles
- 📊 **Interactive Dashboard**: Modern Streamlit UI with dark mode support
- 🌐 **EUR-Lex Integration**: Automated web scraping of EU legal acts
- 📈 **Relevance Scoring**: Advanced scoring algorithm considering multiple factors
- 🎯 **Smart Filtering**: Filter results by document type, relevance score, and categories
- 💾 **Data Management**: SQLite database for storing profiles and legal acts
- 📋 **Detailed Analysis**: Comprehensive reasoning for each legal act's relevance

## Technology Stack

- **Frontend**: Streamlit with custom CSS styling
- **AI/ML**: Hugging Face Transformers, Sentence Transformers
- **Database**: SQLite with pandas integration
- **Web Scraping**: BeautifulSoup, requests
- **Data Processing**: pandas, numpy, scikit-learn
- **Visualization**: Plotly, Streamlit components

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd eu_legal_analyzer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create necessary directories:
```bash
mkdir -p data logs
```

## Usage

### Running the Application

```bash
streamlit run app.py --server.port 12000 --server.address 0.0.0.0
```

The application will be available at `http://localhost:12000`

### Key Workflows

1. **Create Company Profile**:
   - Navigate to "Company Profile" tab
   - Fill in company details, industry, and business activities
   - The system generates embeddings for AI analysis

2. **Scrape Legal Acts**:
   - Go to "Data Management" → "Scraping Tools"
   - Choose to scrape recent acts or by subject area
   - Legal acts are automatically processed and stored

3. **Run Legal Analysis**:
   - Select a company profile in "Legal Analysis"
   - Configure analysis parameters (max results, minimum relevance)
   - View ranked results with detailed reasoning

4. **Review Results**:
   - Filter by document type, relevance score
   - View detailed analysis for each legal act
   - Get compliance recommendations

## AI Models Used

- **Sentence Transformers**: `all-MiniLM-L6-v2` for generating embeddings
- **Summarization**: `facebook/bart-large-cnn` for legal act summaries
- **Classification**: `facebook/bart-large-mnli` for zero-shot classification

## Database Schema

### Legal Acts
- CELEX number, title, document type
- Content, summary, keywords
- Subject matter, dates
- AI-generated embeddings

### Company Profiles
- Company details, industry, size
- Business description and activities
- Compliance areas, risk profile
- AI-generated embeddings

### Analysis Results
- Company-legal act relationships
- Relevance scores and reasoning
- Analysis timestamps

## Configuration

### Environment Variables
- `DB_PATH`: Database file path (default: `data/eu_legal_analyzer.db`)
- `LOG_LEVEL`: Logging level (default: `INFO`)

### Model Configuration
Models are automatically downloaded on first use. Ensure sufficient disk space for:
- Sentence transformer models (~100MB)
- BART models (~1.6GB)

## Features in Detail

### Company Profile Analysis
- Industry-specific legal category mapping
- Business activity keyword extraction
- Risk profile assessment
- Compliance area matching

### Legal Act Processing
- Automated EUR-Lex scraping
- Content extraction and cleaning
- Metadata parsing
- Embedding generation

### Relevance Scoring Algorithm
- **Base Similarity** (40%): Cosine similarity between embeddings
- **Industry Relevance** (30%): Industry-category alignment
- **Content Relevance** (20%): Keyword overlap analysis
- **Recency Factor** (10%): Temporal relevance weighting

### Interactive Features
- Real-time filtering and sorting
- Expandable result cards
- Detailed analysis modals
- Export functionality
- Dark mode support

## API Endpoints

The application uses Streamlit's built-in server. For programmatic access, consider extending with FastAPI:

```python
# Example API extension
from fastapi import FastAPI
from src.models.text_analyzer import TextAnalyzer

app = FastAPI()
analyzer = TextAnalyzer()

@app.post("/analyze")
async def analyze_relevance(company_profile: dict, legal_act: dict):
    return analyzer.analyze_company_legal_relevance(company_profile, legal_act)
```

## Troubleshooting

### Common Issues

1. **Model Download Errors**:
   - Ensure internet connection
   - Check disk space (>2GB required)
   - Verify Hugging Face Hub access

2. **Scraping Issues**:
   - EUR-Lex may have rate limits
   - Check network connectivity
   - Verify website structure hasn't changed

3. **Database Errors**:
   - Ensure write permissions in data directory
   - Check SQLite installation
   - Verify database file integrity

### Performance Optimization

- Use GPU acceleration if available (CUDA)
- Adjust batch sizes for large datasets
- Consider model quantization for memory constraints
- Implement caching for repeated analyses

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is for informational purposes only and should not replace professional legal advice. Always consult with qualified legal professionals for compliance matters.

## Support

For issues and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the logs in the `logs/` directory

## Roadmap

- [ ] Multi-language support
- [ ] Advanced filtering options
- [ ] Email notifications for new relevant acts
- [ ] Integration with legal databases
- [ ] Mobile-responsive design
- [ ] API for third-party integrations
- [ ] Advanced analytics dashboard
- [ ] Compliance timeline tracking