import streamlit as st
import pandas as pd
import json
from sql_ai_agent import SQLAIAgent
import logging

# Configure page
st.set_page_config(
    page_title="SQL AI Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initialize_agent():
    """Initialize the SQL AI Agent with caching"""
    if 'agent' not in st.session_state:
        try:
            with st.spinner("Initializing AI Agent..."):
                st.session_state.agent = SQLAIAgent()
                st.success("✅ AI Agent initialized successfully!")
        except Exception as e:
            st.error(f"❌ Error initializing AI Agent: {e}")
            st.stop()
    return st.session_state.agent

def main():
    """Main Streamlit application"""
    
    # Title and description
    st.title("🤖 SQL AI Agent")
    st.markdown("""
    Welcome to the SQL AI Agent! This tool converts your natural language questions 
    into SQL queries and executes them against your PostgreSQL database.
    """)
    
    # Sidebar
    with st.sidebar:
        st.header("🔧 Configuration")
        
        # Check if environment variables are set
        st.subheader("Environment Status")
        env_status = check_environment()
        for key, status in env_status.items():
            if status:
                st.success(f"✅ {key}")
            else:
                st.error(f"❌ {key}")
        
        # Database Info Section
        if st.button("🔄 Refresh Connection"):
            if 'agent' in st.session_state:
                del st.session_state.agent
            st.rerun()
    
    # Initialize agent
    agent = initialize_agent()
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("💬 Ask Your Question")
        
        # Query input
        user_question = st.text_area(
            "Enter your question about the database:",
            placeholder="e.g., How many customers do we have? Show me sales by month. What's the average order value?",
            height=100,
            key="user_question"
        )
        
        # Example questions
        st.subheader("💡 Example Questions")
        example_questions = [
            "How many records are in each table?",
            "What are the column names for all tables?",
            "Show me the first 5 rows from each table",
            "What's the total count of all records?",
            "Show me the table schema"
        ]
        
        selected_example = st.selectbox(
            "Or select an example question:",
            [""] + example_questions,
            key="example_selector"
        )
        
        if selected_example:
            st.session_state.user_question = selected_example
            user_question = selected_example
        
        # Query execution
        if st.button("🚀 Execute Query", type="primary"):
            if user_question.strip():
                execute_query(agent, user_question)
            else:
                st.warning("Please enter a question or select an example.")
    
    with col2:
        st.header("📊 Database Info")
        
        # Display database information
        display_database_info(agent)
    
    # Query history
    display_query_history()

def check_environment():
    """Check if environment variables are properly set"""
    import os
    
    required_vars = {
        "Azure OpenAI API Key": bool(os.getenv('AZURE_OPENAI_API_KEY')),
        "Azure OpenAI Endpoint": bool(os.getenv('AZURE_OPENAI_ENDPOINT')),
        "Azure Deployment Name": bool(os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME')),
        "Database Host": bool(os.getenv('DB_HOST')),
        "Database Name": bool(os.getenv('DB_NAME')),
        "Database User": bool(os.getenv('DB_USER')),
        "Database Password": bool(os.getenv('DB_PASSWORD'))
    }
    
    return required_vars

def display_database_info(agent):
    """Display database information in the sidebar"""
    try:
        # Get table names
        with st.spinner("Loading database info..."):
            tables = agent.get_table_names()
        
        if tables:
            st.subheader("📋 Available Tables")
            for i, table in enumerate(tables, 1):
                st.write(f"{i}. `{table}`")
            
            # Table selection for sample data
            selected_table = st.selectbox(
                "Select table for sample data:",
                [""] + tables,
                key="table_selector"
            )
            
            if selected_table:
                try:
                    sample_data = agent.get_sample_data(selected_table, 3)
                    if not sample_data.empty:
                        st.subheader(f"📄 Sample Data: {selected_table}")
                        st.dataframe(sample_data, use_container_width=True)
                    else:
                        st.info("No data found in this table.")
                except Exception as e:
                    st.error(f"Error loading sample data: {e}")
        else:
            st.info("No tables found or unable to connect to database.")
            
    except Exception as e:
        st.error(f"Error loading database info: {e}")

def execute_query(agent, question):
    """Execute the user query and display results"""
    
    with st.spinner("🤔 Thinking and generating SQL..."):
        result = agent.query(question)
    
    # Store in session state for history
    if 'query_history' not in st.session_state:
        st.session_state.query_history = []
    
    st.session_state.query_history.append(result)
    
    # Display results
    st.subheader("🎯 Results")
    
    if result['success']:
        # Display agent response
        st.success("✅ Query executed successfully!")
        
        # Display data summary if available
        if result.get('data') is not None:
            row_count = result.get('row_count', 0)
            col_count = result.get('column_count', 0)
            
            # Show summary metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📊 Rows", row_count)
            with col2:
                st.metric("📋 Columns", col_count)
            with col3:
                st.metric("✅ Status", "Success")
        
        # Response
        with st.expander("🤖 AI Agent Response", expanded=True):
            st.write(result['agent_response'])
        
        # SQL Query
        if result.get('sql_query'):
            with st.expander("🔍 Generated SQL Query"):
                st.code(result['sql_query'], language='sql')
        
        # Data Results - prioritize the data from the result
        if result.get('data') is not None:
            data_df = result['data']
            if not data_df.empty:
                with st.expander("📊 Query Results", expanded=True):
                    st.dataframe(data_df, use_container_width=True)
                    
                    # Download button
                    csv = data_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Full Results as CSV",
                        data=csv,
                        file_name=f"query_results_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                    
                    # Data info
                    st.info(f"📈 Showing {len(data_df)} rows × {len(data_df.columns)} columns")
            else:
                st.info("📋 Query executed successfully but returned no data.")
        
        # Fallback: try to execute SQL if data wasn't included in result
        elif result.get('sql_query'):
            try:
                raw_data = agent.execute_raw_sql(result['sql_query'])
                if not raw_data.empty:
                    with st.expander("📊 Query Results", expanded=True):
                        st.dataframe(raw_data, use_container_width=True)
                        
                        # Download button
                        csv = raw_data.to_csv(index=False)
                        st.download_button(
                            label="📥 Download Results as CSV",
                            data=csv,
                            file_name=f"query_results_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
                        
                        st.info(f"📈 Showing {len(raw_data)} rows × {len(raw_data.columns)} columns")
                else:
                    st.info("📋 Query executed successfully but returned no data.")
            except Exception as e:
                st.warning(f"Could not execute SQL for data display: {e}")
        
        # Show any data execution errors
        if result.get('data_execution_error'):
            st.warning(f"⚠️ Note: Could not execute SQL for data preview: {result['data_execution_error']}")
    
    else:
        st.error("❌ Query failed!")
        st.error(result.get('error', 'Unknown error'))

def display_query_history():
    """Display query history"""
    if 'query_history' in st.session_state and st.session_state.query_history:
        st.header("📚 Query History")
        
        # Clear history button
        if st.button("🗑️ Clear History"):
            st.session_state.query_history = []
            st.rerun()
        
        # Display history in reverse order (newest first)
        for i, query in enumerate(reversed(st.session_state.query_history)):
            with st.expander(f"Query {len(st.session_state.query_history) - i}: {query['user_question'][:50]}..."):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**Question:** {query['user_question']}")
                    st.write(f"**Status:** {'✅ Success' if query['success'] else '❌ Failed'}")
                    
                    if query['success']:
                        st.write(f"**Response:** {query['agent_response'][:200]}...")
                        if query.get('sql_query'):
                            st.code(query['sql_query'], language='sql')
                    else:
                        st.write(f"**Error:** {query.get('error', 'Unknown error')}")
                
                with col2:
                    st.write(f"**Time:** {query['timestamp']}")

if __name__ == "__main__":
    main()
