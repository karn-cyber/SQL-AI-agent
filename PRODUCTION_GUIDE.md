# SQL AI Agent - Production Deployment Guide

## 🎯 Overview

This SQL AI Agent converts natural language queries into PostgreSQL SQL queries using Azure OpenAI and LangChain. The agent follows a systematic approach to analyze database structure before generating optimized SQL queries.

## 📋 Prerequisites

### Required Services
1. **Azure OpenAI** - For natural language processing
   - GPT-3.5-turbo or GPT-4 deployment
   - API key and endpoint access

2. **PostgreSQL Database** - Target database
   - Version 12+ recommended
   - Network access from application server

### Required Software
- Python 3.8+
- pip package manager

## 🚀 Quick Setup

### 1. Install Dependencies
```bash
pip install langchain==0.1.16 langchain-openai==0.1.6 langchain-community==0.0.32 sqlalchemy==2.0.29 psycopg2-binary==2.9.9 python-dotenv==1.0.1 pandas==2.2.2 streamlit==1.33.0
```

### 2. Environment Configuration
Create a `.env` file with your credentials:

```env
# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your_azure_openai_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_DEPLOYMENT_NAME=your_gpt_model_deployment_name

# PostgreSQL Database Configuration
DB_HOST=your_postgres_host
DB_PORT=5432
DB_NAME=your_database_name
DB_USER=your_username
DB_PASSWORD=your_password
DB_SSLMODE=prefer
```

### 3. Test Installation
```bash
python test_connection.py  # Test database and API connections
python simple_demo.py     # Test without dependencies
```

## 🏗️ Architecture

### Core Components

1. **SQLAIAgent** (`sql_ai_agent.py`)
   - Main orchestrator class
   - Handles Azure OpenAI integration
   - Manages database connections
   - Processes natural language queries

2. **Configuration** (`config.py`)
   - Database connection management
   - Azure OpenAI configuration
   - Environment variable handling

3. **Interfaces**
   - **Web UI**: `streamlit run streamlit_app.py`
   - **CLI**: `python cli.py`
   - **API**: Import and use SQLAIAgent class

### How It Works

1. **Database Structure Analysis**
   - Agent examines table schemas, relationships, and constraints
   - Identifies relevant tables for the query
   - Understands data types and business rules

2. **Query Generation**
   - Creates PostgreSQL-optimized queries
   - Includes proper error handling and data validation
   - Adds performance optimizations (indexing hints, efficient joins)

3. **Execution & Response**
   - Executes SQL against PostgreSQL database
   - Formats results in human-readable format
   - Provides query explanations and insights

## 💼 Production Usage

### Python API Usage
```python
from sql_ai_agent import SQLAIAgent

# Initialize agent
agent = SQLAIAgent()

# Ask questions
result = agent.query("How many customers do we have by city?")

if result['success']:
    print(f"Answer: {result['agent_response']}")
    print(f"SQL: {result['sql_query']}")
    
    # Execute raw SQL if needed
    df = agent.execute_raw_sql(result['sql_query'])
    print(df)
else:
    print(f"Error: {result['error']}")

# Clean up
agent.close_connection()
```

### Web Interface
```bash
streamlit run streamlit_app.py
```
- User-friendly web interface
- Query history tracking
- Result downloading (CSV)
- Database schema browsing

### Command Line
```bash
python cli.py
```
- Interactive command-line interface
- Perfect for scripting and automation

## 🔧 Advanced Configuration

### Performance Tuning
```python
# In config.py - adjust connection pool settings
engine = create_engine(
    connection_string,
    pool_size=20,        # Increase for high concurrency
    max_overflow=30,     # Handle traffic spikes
    pool_pre_ping=True,  # Validate connections
    echo=False          # Set True for SQL debugging
)
```

### Custom Prompting
The agent uses sophisticated prompts that:
- Analyze database structure first
- Generate PostgreSQL-specific syntax
- Include data quality considerations
- Provide query explanations

### Security Considerations
1. **Database Access**: Use read-only database users when possible
2. **API Keys**: Store securely, rotate regularly
3. **Input Validation**: Agent includes SQL injection protection
4. **Network**: Use SSL connections for database and API calls

## 📊 Example Queries

The agent handles complex queries like:

```sql
-- Age-based filtering with data quality checks
SELECT 
    name, age, city, email
FROM users 
WHERE age > 25 
    AND age IS NOT NULL
ORDER BY age DESC, name ASC;

-- Comprehensive statistics
SELECT 
    AVG(age) as average_age,
    MEDIAN(age) as median_age,
    MIN(age) as youngest_user,
    MAX(age) as oldest_user,
    STDDEV(age) as age_standard_deviation
FROM users 
WHERE age IS NOT NULL AND age > 0 AND age < 150;

-- Complex joins with business logic
SELECT 
    u.name as customer_name,
    u.city,
    COUNT(o.id) as total_orders,
    SUM(o.total_amount) as total_spent,
    AVG(o.total_amount) as avg_order_value
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE o.status IN ('delivered', 'shipped')
GROUP BY u.id, u.name, u.city
HAVING COUNT(o.id) > 0
ORDER BY total_spent DESC;
```

## 🚨 Error Handling

The agent includes comprehensive error handling:
- Database connection failures
- API timeout and rate limiting
- SQL syntax errors
- Data type mismatches
- Network connectivity issues

## 📈 Monitoring & Logging

Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.INFO)
```

Monitor key metrics:
- Query response times
- Database connection health
- API usage and costs
- Error rates

## 🔄 Deployment Options

### Option 1: Direct Deployment
- Deploy Python application directly
- Use systemd for service management
- Set up reverse proxy (nginx) for web interface

### Option 2: Docker Deployment
```bash
docker-compose up  # Includes PostgreSQL for testing
```

### Option 3: Cloud Deployment
- Azure Container Instances
- AWS ECS/Fargate
- Google Cloud Run

## 📋 Production Checklist

### Before Deployment
- [ ] Test with your actual database schema
- [ ] Verify Azure OpenAI quota and limits
- [ ] Configure proper database user permissions
- [ ] Set up SSL certificates for production
- [ ] Configure monitoring and alerting
- [ ] Test error scenarios and recovery

### Security Review
- [ ] Review database access permissions
- [ ] Validate input sanitization
- [ ] Check API key storage and rotation
- [ ] Audit network security settings
- [ ] Review logging for sensitive data

### Performance Testing
- [ ] Test with expected query volume
- [ ] Verify database connection pooling
- [ ] Monitor API response times
- [ ] Test concurrent user scenarios

## 🆘 Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check credentials in .env file
   - Verify network connectivity
   - Confirm PostgreSQL is running

2. **Azure OpenAI Errors**
   - Validate API key and endpoint
   - Check deployment name
   - Verify quota limits

3. **Slow Queries**
   - Review database indexes
   - Optimize complex queries
   - Check connection pool settings

4. **Import Errors**
   - Reinstall requirements: `pip install -r requirements.txt`
   - Check Python version compatibility

## 📞 Support

For issues:
1. Check logs for detailed error messages
2. Verify configuration settings
3. Test individual components (database, API)
4. Review this documentation

## 🎉 Success Metrics

Track these KPIs:
- Query accuracy rate
- Average response time
- User adoption rate
- Cost per query
- Error rate reduction

---

**Ready for Production!** 🚀

This SQL AI Agent provides enterprise-grade natural language to SQL capabilities with proper error handling, security considerations, and performance optimizations.
