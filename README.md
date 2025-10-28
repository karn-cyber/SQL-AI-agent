# SQL AI Agent

AI-powered agent that converts natural language queries into PostgreSQL SQL using Azure OpenAI and LangChain.

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your Azure OpenAI and PostgreSQL credentials
   ```

3. **Test setup:**
   ```bash
   python test_connection.py
   ```

4. **Run application:**
   ```bash
   # Web interface
   streamlit run streamlit_app.py
   
   # Command line
   python cli.py
   
   # Python API
   python sql_ai_agent.py
   ```

## Configuration

Required environment variables in `.env`:

```env
# Azure OpenAI
AZURE_OPENAI_API_KEY=your_api_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# PostgreSQL Database
DB_HOST=your_host
DB_PORT=5432
DB_NAME=your_database
DB_USER=your_username
DB_PASSWORD=your_password
```

## Usage

### Python API
```python
from sql_ai_agent import SQLAIAgent

agent = SQLAIAgent()
result = agent.query("How many users are there?")
print(result['agent_response'])
print(result['sql_query'])
agent.close_connection()
```

### Web Interface
- Navigate to the Streamlit app for a user-friendly GUI
- Ask questions in natural language
- View generated SQL and results
- Download results as CSV

### Command Line
- Interactive CLI for quick queries
- Perfect for scripting and automation

## Architecture

- **sql_ai_agent.py** - Main AI agent class
- **config.py** - Configuration management  
- **streamlit_app.py** - Web interface
- **cli.py** - Command line interface
- **test_connection.py** - Connection testing

## Docker Deployment

```bash
docker-compose up
```

See `PRODUCTION_GUIDE.md` for detailed deployment instructions.

## Features

- ✅ Natural language to SQL conversion
- ✅ PostgreSQL optimization
- ✅ Database structure analysis
- ✅ Error handling and validation
- ✅ Multiple interfaces (Web, CLI, API)
- ✅ Docker support
