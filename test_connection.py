#!/usr/bin/env python3
"""
Simple database schema checker
Use this to test your PostgreSQL connection before running the full AI agent
"""

import os
import sys
from urllib.parse import quote_plus

def test_basic_connection():
    """Test basic database connection using minimal dependencies"""
    print("🔍 Testing basic database connection...")
    
    # Try to import psycopg2
    try:
        import psycopg2
        from psycopg2 import sql
    except ImportError:
        print("❌ psycopg2 not installed. Run: pip install psycopg2-binary")
        return False
    
    # Load environment variables manually
    env_vars = load_env_file()
    
    # Get database configuration
    host = env_vars.get('DB_HOST', 'localhost')
    port = env_vars.get('DB_PORT', '5432')
    database = env_vars.get('DB_NAME')
    user = env_vars.get('DB_USER')
    password = env_vars.get('DB_PASSWORD')
    
    if not all([database, user, password]):
        print("❌ Missing database configuration in .env file")
        print("Required: DB_NAME, DB_USER, DB_PASSWORD")
        return False
    
    try:
        # Create connection
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )
        
        print("✅ Database connection successful!")
        
        # Get basic information
        with conn.cursor() as cursor:
            # Get PostgreSQL version
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            print(f"📊 PostgreSQL version: {version.split()[1]}")
            
            # Get table count
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            table_count = cursor.fetchone()[0]
            print(f"📋 Tables in database: {table_count}")
            
            # Get table names
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
            tables = cursor.fetchall()
            
            if tables:
                print("📝 Available tables:")
                for i, (table,) in enumerate(tables, 1):
                    print(f"  {i}. {table}")
                    
                # Show schema for first table
                if tables:
                    first_table = tables[0][0]
                    cursor.execute("""
                        SELECT column_name, data_type, is_nullable
                        FROM information_schema.columns 
                        WHERE table_name = %s
                        ORDER BY ordinal_position
                    """, (first_table,))
                    
                    columns = cursor.fetchall()
                    if columns:
                        print(f"\n🏗️  Schema for '{first_table}':")
                        for col_name, data_type, is_nullable in columns:
                            nullable = "NULL" if is_nullable == "YES" else "NOT NULL"
                            print(f"  - {col_name}: {data_type} {nullable}")
            else:
                print("⚠️  No tables found in the public schema")
        
        conn.close()
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Database connection failed: {e}")
        print("💡 Check your database configuration in .env file")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def load_env_file():
    """Load environment variables from .env file"""
    env_vars = {}
    
    try:
        with open('.env', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    except FileNotFoundError:
        print("❌ .env file not found!")
        print("💡 Copy .env.example to .env and configure it")
    except Exception as e:
        print(f"❌ Error reading .env file: {e}")
    
    return env_vars

def test_azure_openai_basic():
    """Test basic Azure OpenAI configuration"""
    print("\n🤖 Testing Azure OpenAI configuration...")
    
    env_vars = load_env_file()
    
    required_vars = [
        'AZURE_OPENAI_API_KEY',
        'AZURE_OPENAI_ENDPOINT',
        'AZURE_OPENAI_DEPLOYMENT_NAME'
    ]
    
    missing = []
    for var in required_vars:
        if not env_vars.get(var) or 'your_' in env_vars.get(var, ''):
            missing.append(var)
    
    if missing:
        print(f"❌ Missing or incomplete Azure OpenAI configuration: {', '.join(missing)}")
        return False
    
    print("✅ Azure OpenAI configuration looks complete")
    print(f"📡 Endpoint: {env_vars['AZURE_OPENAI_ENDPOINT']}")
    print(f"🚀 Deployment: {env_vars['AZURE_OPENAI_DEPLOYMENT_NAME']}")
    
    return True

def create_sample_data():
    """Create sample data for testing (optional)"""
    print("\n📊 Would you like to create sample data for testing?")
    response = input("This will create a 'sample_users' table with test data (y/N): ").strip().lower()
    
    if response not in ['y', 'yes']:
        return
    
    try:
        import psycopg2
        env_vars = load_env_file()
        
        conn = psycopg2.connect(
            host=env_vars.get('DB_HOST', 'localhost'),
            port=env_vars.get('DB_PORT', '5432'),
            database=env_vars.get('DB_NAME'),
            user=env_vars.get('DB_USER'),
            password=env_vars.get('DB_PASSWORD')
        )
        
        with conn.cursor() as cursor:
            # Create sample table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sample_users (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    email VARCHAR(150) UNIQUE NOT NULL,
                    age INTEGER,
                    city VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Insert sample data
            cursor.execute("""
                INSERT INTO sample_users (name, email, age, city) VALUES
                ('John Doe', 'john.doe@example.com', 30, 'New York'),
                ('Jane Smith', 'jane.smith@example.com', 25, 'Los Angeles'),
                ('Bob Johnson', 'bob.johnson@example.com', 35, 'Chicago'),
                ('Alice Brown', 'alice.brown@example.com', 28, 'Houston'),
                ('Charlie Wilson', 'charlie.wilson@example.com', 32, 'Phoenix')
                ON CONFLICT (email) DO NOTHING
            """)
            
            conn.commit()
            print("✅ Sample data created successfully!")
            print("🎯 You can now test queries like:")
            print("  - 'How many users are there?'")
            print("  - 'Show me all users from New York'")
            print("  - 'What's the average age of users?'")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")

def main():
    """Main function"""
    print("🧪 SQL AI Agent - Connection Tester")
    print("=" * 50)
    print("This script tests your database and Azure OpenAI configuration")
    print("before running the full AI agent.")
    print("=" * 50)
    
    # Test database connection
    db_success = test_basic_connection()
    
    # Test Azure OpenAI configuration
    azure_success = test_azure_openai_basic()
    
    print("\n" + "=" * 50)
    if db_success and azure_success:
        print("🎉 All basic tests passed!")
        print("✅ Your configuration looks good for running the SQL AI Agent")
        
        # Offer to create sample data
        create_sample_data()
        
        print("\n🚀 Next steps:")
        print("  python demo.py                 # Run demo")
        print("  streamlit run streamlit_app.py # Web interface") 
        print("  python cli.py                  # Command line")
        
    else:
        print("❌ Some tests failed")
        print("📝 Please fix the configuration issues above")
        
        if not db_success:
            print("\n💡 Database troubleshooting:")
            print("  - Ensure PostgreSQL is running")
            print("  - Check host, port, database name")
            print("  - Verify username and password")
            print("  - Check firewall/network connectivity")
        
        if not azure_success:
            print("\n💡 Azure OpenAI troubleshooting:")
            print("  - Get API key from Azure Portal")
            print("  - Check endpoint URL format")
            print("  - Verify deployment name")
            print("  - Ensure deployment is active")

if __name__ == "__main__":
    main()
