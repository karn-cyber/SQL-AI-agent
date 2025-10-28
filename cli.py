#!/usr/bin/env python3
"""
Simple command-line interface for the SQL AI Agent
Run this script to interact with the SQL AI Agent via command line
"""

import sys
import os
from sql_ai_agent import SQLAIAgent

def main():
    """Main CLI function"""
    print("🤖 SQL AI Agent - Command Line Interface")
    print("=" * 50)
    print("This tool converts natural language to SQL queries and executes them.")
    print("Type 'quit', 'exit', or 'q' to exit the program.")
    print("Type 'help' for example questions.")
    print("=" * 50)
    
    try:
        # Initialize the agent
        print("\n🔄 Initializing AI Agent...")
        agent = SQLAIAgent()
        print("✅ AI Agent initialized successfully!")
        
        # Display database info
        print(f"\n📊 Database Info:")
        tables = agent.get_table_names()
        if tables:
            print(f"Available tables: {', '.join(tables)}")
        else:
            print("No tables found or unable to access database.")
        
        # Main interaction loop
        while True:
            try:
                # Get user input
                print("\n" + "-" * 50)
                user_input = input("\n💬 Enter your question: ").strip()
                
                # Check for exit commands
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Goodbye!")
                    break
                
                # Check for help
                if user_input.lower() == 'help':
                    show_help()
                    continue
                
                # Check for empty input
                if not user_input:
                    print("❌ Please enter a question.")
                    continue
                
                # Process the query
                print(f"\n🤔 Processing: {user_input}")
                print("⏳ Please wait...")
                
                result = agent.query(user_input)
                
                # Display results
                print("\n" + "=" * 50)
                if result['success']:
                    print("✅ SUCCESS!")
                    print(f"\n🤖 AI Response:")
                    print(result['agent_response'])
                    
                    if result.get('sql_query'):
                        print(f"\n🔍 Generated SQL:")
                        print(result['sql_query'])
                        
                        # Ask if user wants to see raw data
                        try:
                            show_data = input("\n📊 Show raw query results? (y/n): ").strip().lower()
                            if show_data in ['y', 'yes']:
                                raw_data = agent.execute_raw_sql(result['sql_query'])
                                if not raw_data.empty:
                                    print(f"\n📋 Raw Results ({len(raw_data)} rows):")
                                    print(raw_data.to_string(max_rows=20, max_cols=10))
                                    if len(raw_data) > 20:
                                        print(f"... and {len(raw_data) - 20} more rows")
                                else:
                                    print("No data returned from query.")
                        except Exception as e:
                            print(f"⚠️ Could not display raw data: {e}")
                else:
                    print("❌ FAILED!")
                    print(f"Error: {result.get('error', 'Unknown error')}")
                
                print("=" * 50)
                
            except KeyboardInterrupt:
                print("\n\n👋 Interrupted by user. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error processing query: {e}")
                continue
    
    except Exception as e:
        print(f"\n❌ Failed to initialize AI Agent: {e}")
        print("\n💡 Make sure your .env file is configured correctly.")
        sys.exit(1)
    
    finally:
        # Clean up
        try:
            if 'agent' in locals():
                agent.close_connection()
                print("🔒 Database connection closed.")
        except:
            pass

def show_help():
    """Display help information with example questions"""
    print("\n" + "=" * 50)
    print("💡 HELP - Example Questions")
    print("=" * 50)
    
    examples = [
        "How many records are in each table?",
        "What are the column names and types for all tables?",
        "Show me sample data from the users table",
        "What's the total number of customers?",
        "Show me the database schema",
        "List all table names",
        "What are the most recent 10 records?",
        "Show me records where status is active",
        "What's the average value in the price column?",
        "Count records by category"
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"{i:2d}. {example}")
    
    print("\n💡 Tips:")
    print("- Be specific about which table or columns you're interested in")
    print("- Ask about data analysis, counts, averages, filtering, etc.")
    print("- The AI will first understand your question, then generate appropriate SQL")
    print("=" * 50)

if __name__ == "__main__":
    main()
