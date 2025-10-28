import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseConfig:
    """Database configuration and connection manager"""
    
    def __init__(self):
        self.host = os.getenv('DB_HOST', 'localhost')
        self.port = os.getenv('DB_PORT', '5432')
        self.database = os.getenv('DB_NAME')
        self.username = os.getenv('DB_USER')
        self.password = os.getenv('DB_PASSWORD')
        self.sslmode = os.getenv('DB_SSLMODE', 'prefer')
        
        # Validate required parameters
        if not all([self.database, self.username, self.password]):
            raise ValueError("Missing required database configuration. Please check your .env file.")
    
    def get_connection_string(self) -> str:
        """Generate PostgreSQL connection string"""
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}?sslmode={self.sslmode}"
    
    def create_engine(self):
        """Create and return SQLAlchemy engine"""
        try:
            connection_string = self.get_connection_string()
            engine = create_engine(
                connection_string,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,
                echo=False  # Set to True for SQL query logging
            )
            
            # Test connection
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            logger.info("Database connection established successfully")
            return engine
            
        except SQLAlchemyError as e:
            logger.error(f"Database connection error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error creating database engine: {e}")
            raise

class AzureOpenAIConfig:
    """Azure OpenAI configuration manager"""
    
    def __init__(self):
        self.api_key = os.getenv('AZURE_OPENAI_API_KEY')
        self.endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
        self.api_version = os.getenv('AZURE_OPENAI_API_VERSION', '2024-02-15-preview')
        self.deployment_name = os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME')
        
        # Validate required parameters
        if not all([self.api_key, self.endpoint, self.deployment_name]):
            raise ValueError("Missing required Azure OpenAI configuration. Please check your .env file.")
    
    def get_config(self) -> dict:
        """Return Azure OpenAI configuration as dictionary"""
        return {
            'api_key': self.api_key,
            'azure_endpoint': self.endpoint,
            'api_version': self.api_version,
            'deployment_name': self.deployment_name
        }
