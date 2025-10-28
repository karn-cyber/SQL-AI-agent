#!/usr/bin/env python3
"""
Test script to demonstrate the enhanced SQL AI Agent with data results
This script shows how the agent now returns actual query results along with SQL
"""

import json
from sql_ai_agent import SQLAIAgent
import pandas as pd

def test_query_with_results():
    """Test the enhanced query functionality that returns data"""
    
    print("🧪 Testing Enhanced SQL AI Agent - Query Results Demo")
    print("=" * 60)
    
    try:
        # Initialize agent
        print("🔄 Initializing AI Agent...")
        agent = SQLAIAgent()
        print("✅ AI Agent initialized successfully!")
        
        # Test questions that should return data
        test_questions = [
            "How many records are in each table?",
            "Show me the first 5 rows from any available table",
            "What are all the table names in the database?",
            "Give me a sample of data from the database"
        ]
        
        for i, question in enumerate(test_questions, 1):
            print(f"\n{'='*60}")
            print(f"🔍 Test {i}: {question}")
            print('='*60)
            
            # Execute query
            result = agent.query(question)
            
            # Display results
            if result['success']:
                print("✅ SUCCESS!")
                print(f"\n🤖 AI Response (first 200 chars):")
                print(result['agent_response'][:200] + "..." if len(result['agent_response']) > 200 else result['agent_response'])
                
                if result.get('sql_query'):
                    print(f"\n🔍 Generated SQL:")
                    print(result['sql_query'])
                
                # Show data results
                if result.get('data') is not None:
                    data_df = result['data']
                    row_count = result.get('row_count', 0)
                    col_count = result.get('column_count', 0)
                    
                    print(f"\n📊 Data Summary:")
                    print(f"   Rows: {row_count}")
                    print(f"   Columns: {col_count}")
                    
                    if not data_df.empty:
                        print(f"\n📋 Data Preview (first 5 rows):")
                        print(data_df.head().to_string())
                        
                        if len(data_df) > 5:
                            print(f"... and {len(data_df) - 5} more rows")
                    else:
                        print("📋 Query returned no data")
                        
                if result.get('data_execution_error'):
                    print(f"\n⚠️ Data execution error: {result['data_execution_error']}")
                    
            else:
                print("❌ FAILED!")
                print(f"Error: {result.get('error', 'Unknown error')}")
            
            print("\n" + "-" * 40)
        
        # Test direct SQL execution
        print(f"\n{'='*60}")
        print("🔍 Testing Direct SQL Execution")
        print('='*60)
        
        try:
            # Get table names first
            tables = agent.get_table_names()
            if tables:
                # Try to get sample data from first table
                sample_sql = f"SELECT * FROM {tables[0]} LIMIT 3"
                print(f"Executing: {sample_sql}")
                
                sample_data = agent.execute_raw_sql(sample_sql)
                print(f"✅ Executed successfully - {len(sample_data)} rows returned")
                
                if not sample_data.empty:
                    print("Sample data:")
                    print(sample_data.to_string())
                else:
                    print("No data in table")
            else:
                print("No tables found in database")
                
        except Exception as e:
            print(f"⚠️ Error with direct SQL execution: {e}")
        
        # Clean up
        agent.close_connection()
        print(f"\n🎉 Test completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        print("\n💡 Make sure your .env file is configured correctly.")

def demo_result_structure():
    """Show the structure of the enhanced result object"""
    print(f"\n{'='*60}")
    print("📋 Enhanced Result Structure Demo")
    print('='*60)
    
    sample_result = {
        'success': True,
        'user_question': 'Sample question',
        'agent_response': 'AI agent response with explanation',
        'sql_query': 'SELECT * FROM table_name LIMIT 10;',
        'data': 'pandas.DataFrame with actual results',
        'data_preview': 'pandas.DataFrame with first 10 rows',
        'row_count': 25,
        'column_count': 5,
        'timestamp': '2024-01-01T12:00:00'
    }
    
    print("The enhanced query() method now returns:")
    print(json.dumps(sample_result, indent=2, default=str))
    print("\nKey enhancements:")
    print("✅ 'data': Full pandas DataFrame with query results")
    print("✅ 'data_preview': First 10 rows for quick display")  
    print("✅ 'row_count': Number of rows returned")
    print("✅ 'column_count': Number of columns in results")
    print("✅ Automatic SQL execution when query is extracted")

if __name__ == "__main__":
    # Show the enhanced structure first
    demo_result_structure()
    
    # Run the actual tests
    test_query_with_results()
