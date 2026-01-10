import pyodbc
from sqlalchemy import create_engine, inspect, URL, text
from llama_index.core import SQLDatabase
from llama_index.core.query_engine import NLSQLTableQueryEngine
from llama_index.llms.ollama import Ollama
import time
import logging

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MSSQL connection settings
server = "ZELIS\\REEDUS"
database = "TWD_Database"
username = "sa"
password = "daryldixon"
driver = "ODBC Driver 17 for SQL Server"
schema = "dbo"

# SQLAlchemy connection URL
connection_url = URL.create(
    "mssql+pyodbc",
    username=username,
    password=password,
    host=server,
    database=database,
    query={"driver": driver}
)

try:
    # Create engine
    engine = create_engine(connection_url)
    logger.info("Database connection established successfully")
    
    # Check available tables
    inspector = inspect(engine)
    available_tables = inspector.get_table_names(schema=schema)
    logger.info(f"Available tables: {available_tables}")

    # Check for required tables
    required_tables = {"characters", "appearances"}
    missing_tables = required_tables - set(available_tables)
    if missing_tables:
        logger.warning(f"Missing tables - {missing_tables}")
        raise ValueError(f"Required tables missing: {missing_tables}")

    # SQLDatabase wrapper
    sql_database = SQLDatabase(
        engine,
        include_tables=list(required_tables),
        schema=schema
    )

    # Optimized system prompt for SQL generation
    sql_prompt = (
        "You are a SQL expert for The Walking Dead database. Strictly follow these rules:\n"
        "1. Use EXACT table/column names from schema:\n"
        "   - characters: [id, name, status, species, gender]\n"
        "   - appearances: [id, character_id, episode, season]\n"
        "2. Always use explicit JOIN syntax with aliases:\n"
        "   - characters.id = appearances.character_id\n"
        "3. Use parameterized WHERE clauses: WHERE name = 'Aaron' (EXACT name match)\n"
        "4. NEVER use LIKE unless specified\n"
        "5. Select ONLY necessary columns\n"
        "6. Handle NULL values with IS NULL/IS NOT NULL\n"
        "7. Return raw SQL ONLY, no explanations\n\n"
        "User question: {user_query}\nSQL:"
    )

    # Configure Ollama LLM with enhanced instructions
    llm = Ollama(
        model="gemma3n",
        request_timeout=120.0,
        system_prompt=sql_prompt,
        temperature=0.1  # Reduce creativity for precise SQL
    )

    # Create query engine with schema context
    query_engine = NLSQLTableQueryEngine(
        sql_database=sql_database,
        tables=list(required_tables),
        llm=llm,
        synthesize_response=False  # We'll handle response formatting
    )

    print("\nSystem ready. Ask about The Walking Dead characters and appearances.")
    print("Type 'exit' to quit.\n")

    def format_sql_result(result):
        """Format SQL result for better readability"""
        if not result:
            return "No results found"
        
        if isinstance(result, list):
            if len(result) == 1 and isinstance(result[0], tuple) and len(result[0]) == 1:
                return str(result[0][0])  # Single value
            return "\n".join([str(row) for row in result])
        return str(result)

    while True:
        try:
            user_query = input("\nYour query: ").strip()
            if user_query.lower() in ['exit', 'quit']:
                break
            if not user_query:
                continue

            logger.info(f"Query: {user_query}")
            start_time = time.time()
            
            # Execute query
            response = query_engine.query(user_query)
            exec_time = time.time() - start_time

            # Extract and format results
            sql_query = response.metadata.get('sql_query', '')
            result = response.metadata.get('result', [])
            
            print(f"\nResponse ({exec_time:.2f}s):")
            print(format_sql_result(result))
            
            if sql_query:
                print(f"\nGenerated SQL: {sql_query}")
            else:
                print("\nNo SQL generated")

        except Exception as e:
            logger.error(f"Query failed: {str(e)}")
            print(f"\nError: Could not process query. Please try rephrasing")

    print("Exiting...")

except Exception as e:
    logger.exception("Critical initialization error:")
    print(f"System error: {str(e)}")