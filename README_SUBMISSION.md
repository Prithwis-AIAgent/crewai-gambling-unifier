# Gambling Unifier - CrewAI Implementation

## Project Overview

The Gambling Unifier is a sophisticated multi-agent system built with CrewAI that unifies gambling products from multiple prediction markets. This system demonstrates advanced AI agent collaboration, web scraping, data unification, and intelligent analysis capabilities.

## 🚀 Key Features

- **Multi-Agent Collaboration**: Four specialized agents working together in a sequential workflow
- **Web Scraping Tools**: Automated data collection from multiple gambling platforms
- **Product Unification**: Intelligent matching of products across different sites with confidence scoring
- **Data Export**: Clean CSV generation and comprehensive reporting
- **RAG Integration**: Retrieval-Augmented Generation for intelligent querying and insights
- **Interactive Chat**: User-friendly interface for exploring the unified data

## 🏗️ Architecture

### Agents

1. **Researcher Agent** - Data Collection Specialist
   - Scrapes Polymarket, Kalshi, and other prediction markets
   - Ensures data quality and handles errors gracefully
   - Returns structured JSON arrays of products

2. **Analyst Agent** - Product Unification Expert
   - Matches products across different platforms
   - Computes confidence scores for matches
   - Generates unified datasets ready for analysis

3. **CSV Agent** - Data Export Specialist
   - Creates clean, well-formatted CSV files
   - Maintains data integrity and structure
   - Ensures export compatibility

4. **RAG Agent** - Intelligent Query Assistant
   - Provides insights about unified gambling products
   - Answers questions using the generated data
   - Demonstrates advanced AI analysis capabilities

### Workflow

```
Data Collection → Product Unification → CSV Generation → RAG Analysis
     ↓                ↓                    ↓              ↓
Researcher      Analyst Agent        CSV Agent      RAG Agent
  Agent
```

## 🛠️ Installation & Setup

### Prerequisites

- Python 3.8+
- OpenAI API key
- Internet connection for web scraping

### Dependencies

```bash
pip install crewai langchain-openai python-dotenv
```

### Environment Setup

1. Set your OpenAI API key:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

2. Or create a `.env` file:
```env
OPENAI_API_KEY=your-api-key-here
```

## 📖 Usage

### Basic Execution

Run the complete workflow:

```bash
python crewai_submission.py
```

This will:
1. Execute the full multi-agent workflow
2. Generate output files in the `output/` directory
3. Offer interactive chat with the RAG system

### Output Files

The system generates several output files:

- `raw_products.json` - Raw scraped data from all sources
- `unified_products.csv` - Initial unified product data
- `final_products.csv` - Clean, formatted final CSV
- `rag_analysis.md` - Sample RAG analysis output
- `execution_summary.json` - Complete workflow summary

### Interactive Chat

After the main workflow completes, you can interact with the RAG system:

```
🤖 Gambling Unifier RAG Chat Interface
==================================================
Ask questions about the unified gambling products!
Type 'quit' to exit

You: What are the most popular betting markets?
🤖 Analyzing your question...

🤖 Based on the unified data, the most popular betting markets are...
```

## 🔧 Customization

### Adding New Data Sources

To add new gambling platforms:

1. Create a new scraping tool in `src/gambling_unifier/tools/`
2. Add it to the researcher agent's tools list
3. Update the research task description

### Modifying Agent Behavior

Each agent can be customized by modifying:
- Role descriptions
- Goals and backstories
- Tool assignments
- LLM parameters

### Workflow Changes

The sequential workflow can be modified to:
- Run agents in parallel where appropriate
- Add new tasks or modify existing ones
- Change the execution order

## 📊 Data Structure

### Product Schema

```python
@dataclass
class GamblingProduct:
    site: str              # Source platform
    product_id: str        # Unique identifier
    name: str             # Product name
    price: Optional[float] # Current price
    url: str              # Product URL
    confidence: Optional[float] = None  # Match confidence
```

### CSV Output Format

The final CSV contains columns:
- `name` - Product name
- `site` - Source platform
- `product_id` - Unique identifier
- `price` - Current price
- `confidence` - Match confidence score

## 🧪 Testing & Validation

### Running Tests

```bash
# Test individual components
python -m pytest tests/

# Test the full workflow
python crewai_submission.py
```

### Validation Checks

The system includes several validation mechanisms:
- Data quality checks during scraping
- Confidence scoring for product matches
- Output format validation
- Error handling and logging

## 📈 Performance & Scalability

### Current Capabilities

- Handles 3+ gambling platforms simultaneously
- Processes hundreds of products efficiently
- Generates results in minutes
- Maintains data quality throughout the pipeline

### Scalability Features

- Modular agent architecture
- Configurable LLM models
- Extensible tool system
- Memory-efficient processing

## 🔒 Security & Ethics

### Data Handling

- No personal data collection
- Public gambling market information only
- Secure API key management
- Logging for audit trails

### Ethical Considerations

- Respects website terms of service
- Rate limiting to avoid overwhelming servers
- Transparent data processing
- Responsible AI usage

## 🚨 Troubleshooting

### Common Issues

1. **API Key Errors**
   - Ensure `OPENAI_API_KEY` is set correctly
   - Check API key validity and quota

2. **Scraping Failures**
   - Verify internet connectivity
   - Check if target sites are accessible
   - Review error logs for specific issues

3. **Memory Issues**
   - Reduce batch sizes for large datasets
   - Use smaller LLM models if needed

### Debug Mode

Enable verbose logging by setting:
```python
logging.getLogger().setLevel(logging.DEBUG)
```

## 📚 Technical Details

### CrewAI Features Used

- **Sequential Processing**: Tasks execute in order with context passing
- **Agent Memory**: Persistent context across task executions
- **Tool Integration**: Custom tools for specialized functionality
- **Output Management**: Structured file generation and tracking

### LLM Configuration

- **Model**: GPT-4 (configurable)
- **Temperature**: 0.1 (low randomness for consistency)
- **Context Window**: Handles large datasets efficiently

## 🎯 Future Enhancements

### Planned Features

- Real-time data updates
- Additional gambling platforms
- Advanced analytics dashboard
- Machine learning-based matching
- API endpoints for integration

### Contributing

Contributions are welcome! Areas for improvement:
- New data sources
- Enhanced matching algorithms
- Performance optimizations
- Additional analysis tools

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Authors

- **Primary Developer**: [Your Name]
- **CrewAI Framework**: CrewAI Team
- **Contributors**: [List any contributors]

## 🙏 Acknowledgments

- CrewAI team for the excellent framework
- OpenAI for LLM capabilities
- The open-source community for tools and libraries

---

**Note**: This is a demonstration project showcasing CrewAI capabilities. Please ensure compliance with all applicable laws and terms of service when using web scraping tools.
