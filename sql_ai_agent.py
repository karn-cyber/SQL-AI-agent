import os
import logging
from typing import List, Dict, Any, Optional
from config import DatabaseConfig, AzureOpenAIConfig
from langchain_openai import AzureChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain.agents import create_sql_agent, AgentType
from langchain.schema import BaseMessage
from sqlalchemy import text
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SQLAIAgent:
    """
    AI Agent that processes natural language queries and converts them to SQL queries
    for PostgreSQL database using Azure OpenAI and LangChain
    """
    
    def __init__(self):
        """Initialize the SQL AI Agent"""
        try:
            # Load configurations
            self.db_config = DatabaseConfig()
            self.azure_config = AzureOpenAIConfig()
            
            # Initialize Azure OpenAI LLM
            self.llm = self._initialize_llm()
            
            # Initialize database connection
            self.engine = self.db_config.create_engine()
            self.sql_database = SQLDatabase(self.engine)
            
            # Initialize SQL toolkit and agent
            self.toolkit = SQLDatabaseToolkit(db=self.sql_database, llm=self.llm)
            self.agent = self._create_agent()
            
            logger.info("SQL AI Agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing SQL AI Agent: {e}")
            raise
    
    def _initialize_llm(self) -> AzureChatOpenAI:
        """Initialize Azure OpenAI LLM"""
        try:
            azure_config = self.azure_config.get_config()
            
            llm = AzureChatOpenAI(
                azure_endpoint=azure_config['azure_endpoint'],
                api_key=azure_config['api_key'],
                api_version=azure_config['api_version'],
                deployment_name=azure_config['deployment_name'],
                temperature=0,  # Low temperature for consistent SQL generation
                max_tokens=1000,
                timeout=60
            )
            
            logger.info("Azure OpenAI LLM initialized successfully")
            return llm
            
        except Exception as e:
            logger.error(f"Error initializing Azure OpenAI LLM: {e}")
            raise
    
    def _create_agent(self):
        """Create SQL agent with tools"""
        try:
            agent = create_sql_agent(
                llm=self.llm,
                toolkit=self.toolkit,
                verbose=True,
                agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                handle_parsing_errors=True,
                max_iterations=5,
                early_stopping_method="generate"
            )
            
            logger.info("SQL Agent created successfully")
            return agent
            
        except Exception as e:
            logger.error(f"Error creating SQL agent: {e}")
            raise
    
    def get_database_schema(self) -> str:
        """Get database schema information"""
        try:
            schema_info = self.sql_database.get_table_info()
            return schema_info
        except Exception as e:
            logger.error(f"Error getting database schema: {e}")
            return "Error retrieving schema information"
    
    def get_table_names(self) -> List[str]:
        """Get list of table names in the database"""
        try:
            return self.sql_database.get_usable_table_names()
        except Exception as e:
            logger.error(f"Error getting table names: {e}")
            return []
    
    def execute_raw_sql(self, sql_query: str) -> pd.DataFrame:
        """Execute raw SQL query and return results as DataFrame"""
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text(sql_query))
                df = pd.DataFrame(result.fetchall(), columns=result.keys())
                return df
        except Exception as e:
            logger.error(f"Error executing raw SQL: {e}")
            raise
    
    def query(self, user_question: str) -> Dict[str, Any]:
        """
        Process user question and return SQL query with results
        
        Args:
            user_question (str): Natural language question about the database
            
        Returns:
            Dict containing the response, SQL query (if extracted), results data, and metadata
        """
        try:
            logger.info(f"Processing user question: {user_question}")
            
            # Enhanced prompt with proper database analysis methodology
            enhanced_prompt = f"""
            You are an expert SQL analyst working with a PostgreSQL database. Please answer this question: {user_question}

            Follow this systematic approach:

            1. ANALYZE DATABASE STRUCTURE FIRST:
               - Examine the available tables and their relationships
               - Understand the column names, data types, and constraints
               - Identify primary keys, foreign keys, and indexes
               - Use the SQL database tools to inspect the schema

            2. UNDERSTAND THE BUSINESS QUESTION:
               - Parse what the user is asking for specifically
               - Identify which tables and columns are relevant
               - Determine what type of analysis is needed (count, aggregation, filtering, joining, etc.)

            3. GENERATE PROPER POSTGRESQL QUERIES:
               - Write well-structured, efficient SQL queries
               - Include proper WHERE clauses, JOINs, and ORDER BY as needed
               - Handle NULL values and data quality considerations
               - Use PostgreSQL-specific functions when appropriate (e.g., LIMIT, COALESCE, etc.)
               - Add comments explaining the query logic

            4. EXECUTE AND INTERPRET RESULTS:
               - Run the SQL query against the database
               - Provide a clear, human-readable interpretation of the results
               - Include relevant statistics and insights

            5. ENSURE DATA QUALITY:
               - Check for and handle NULL values appropriately
               - Validate that results make business sense
               - Consider edge cases and data anomalies

            Please be thorough in your analysis and provide detailed explanations of your approach.
            The user should understand both what data was found and how you found it.
            """
            
            # Execute the agent
            response = self.agent.invoke({"input": enhanced_prompt})
            
            # Extract the output
            agent_output = response.get('output', '')
            sql_query = self._extract_sql_from_response(agent_output)
            
            # Initialize result structure
            result = {
                'success': True,
                'user_question': user_question,
                'agent_response': agent_output,
                'sql_query': sql_query,
                'data': None,
                'data_preview': None,
                'row_count': 0,
                'column_count': 0,
                'timestamp': pd.Timestamp.now().isoformat()
            }
            
            # If we extracted a SQL query, execute it and get the actual data
            if sql_query:
                try:
                    logger.info(f"Executing extracted SQL query: {sql_query}")
                    data_df = self.execute_raw_sql(sql_query)
                    
                    # Add data information to result
                    result['data'] = data_df
                    result['row_count'] = len(data_df)
                    result['column_count'] = len(data_df.columns) if not data_df.empty else 0
                    
                    # Create a preview (first 10 rows) for display
                    if not data_df.empty:
                        result['data_preview'] = data_df.head(10)
                        logger.info(f"Query returned {len(data_df)} rows and {len(data_df.columns)} columns")
                    else:
                        result['data_preview'] = pd.DataFrame()
                        logger.info("Query returned no data")
                    
                except Exception as e:
                    logger.warning(f"Could not execute extracted SQL query: {e}")
                    result['data_execution_error'] = str(e)
            
            logger.info("Query processed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                'success': False,
                'user_question': user_question,
                'error': str(e),
                'timestamp': pd.Timestamp.now().isoformat()
            }
    
    def _extract_sql_from_response(self, response: str) -> Optional[str]:
        """Extract SQL query from agent response with improved parsing"""
        try:
            # Look for SQL queries in the response with multiple patterns
            lines = response.split('\n')
            sql_lines = []
            in_sql_block = False
            in_code_block = False
            
            for line in lines:
                line_stripped = line.strip()
                
                # Check for code block markers
                if line_stripped.startswith('```sql') or line_stripped.startswith('```SQL'):
                    in_code_block = True
                    continue
                elif line_stripped == '```' and in_code_block:
                    in_code_block = False
                    break
                elif in_code_block:
                    sql_lines.append(line)
                    continue
                
                # Check for SQL keywords at the start of lines
                sql_keywords = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'WITH', 'CREATE', 'ALTER', 'DROP']
                if any(line_stripped.upper().startswith(keyword) for keyword in sql_keywords):
                    in_sql_block = True
                    sql_lines.append(line)
                elif in_sql_block:
                    # Continue collecting SQL lines until we hit a non-SQL line or semicolon
                    if line_stripped.endswith(';'):
                        sql_lines.append(line)
                        break
                    elif line_stripped == '' or line_stripped.startswith('--'):
                        # Include empty lines and comments in SQL
                        sql_lines.append(line)
                    elif any(keyword in line_stripped.upper() for keyword in ['FROM', 'WHERE', 'JOIN', 'GROUP BY', 'ORDER BY', 'HAVING', 'UNION', 'LIMIT']):
                        # SQL continuation keywords
                        sql_lines.append(line)
                    elif line_stripped and not any(char in line_stripped for char in ['(', ')', ',', '=', '<', '>', "'", '"']) and not line_stripped.replace(' ', '').replace('\t', '').isalnum():
                        # Likely not SQL anymore
                        break
                    else:
                        sql_lines.append(line)
            
            if sql_lines:
                # Clean up the SQL
                sql_query = '\n'.join(sql_lines).strip()
                
                # Remove common non-SQL prefixes
                prefixes_to_remove = [
                    'Here\'s the SQL query:',
                    'SQL Query:',
                    'Query:',
                    'The SQL query is:',
                    'Let me run this query:'
                ]
                
                for prefix in prefixes_to_remove:
                    if sql_query.startswith(prefix):
                        sql_query = sql_query[len(prefix):].strip()
                
                # Ensure query ends with semicolon if it doesn't already
                if sql_query and not sql_query.rstrip().endswith(';'):
                    sql_query = sql_query.rstrip() + ';'
                
                return sql_query if sql_query else None
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting SQL from response: {e}")
            return None
    
    def get_sample_data(self, table_name: str, limit: int = 5) -> pd.DataFrame:
        """Get sample data from a specific table"""
        try:
            query = f"SELECT * FROM {table_name} LIMIT {limit}"
            return self.execute_raw_sql(query)
        except Exception as e:
            logger.error(f"Error getting sample data from {table_name}: {e}")
            return pd.DataFrame()
    
    def close_connection(self):
        """Close database connection"""
        try:
            if hasattr(self, 'engine'):
                self.engine.dispose()
                logger.info("Database connection closed")
        except Exception as e:
            logger.error(f"Error closing database connection: {e}")

# Example usage and testing functions
def test_agent():
    """Test function to demonstrate agent capabilities"""
    try:
        # Initialize agent
        agent = SQLAIAgent()
        
        # Test database connection
        print("Database Tables:", agent.get_table_names())
        print("\nDatabase Schema:\n", agent.get_database_schema()[:500] + "...")
        
        # Test queries
        test_questions = [
            "How many records are in each table?",
            "What are the column names and types for all tables?",
            "Show me sample data from the first table"
        ]
        
        for question in test_questions:
            print(f"\n{'='*50}")
            print(f"Question: {question}")
            print(f"{'='*50}")
            
            result = agent.query(question)
            
            if result['success']:
                print(f"Response: {result['agent_response']}")
                if result['sql_query']:
                    print(f"SQL Query: {result['sql_query']}")
            else:
                print(f"Error: {result['error']}")
        
        # Clean up
        agent.close_connection()
        
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    test_agent()
