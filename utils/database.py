import os
from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

load_dotenv()

# Use DATABASE_URL from environment, fallback to local sqlite for testing
DB_URL = os.environ.get("DATABASE_URL", "sqlite:///employee_data.db")
engine = create_engine(DB_URL)

def get_db_schema() -> str:
    """
    Connects to the database and retrieves the schema for context
    using SQLAlchemy metadata (supports Postgres, SQLite, MySQL, etc).
    """
    try:
        metadata = MetaData()
        metadata.reflect(bind=engine)
        
        schema_text = ""
        for table_name, table in metadata.tables.items():
            schema_text += f"-- Table: {table_name}\\n"
            columns = []
            for column in table.columns:
                columns.append(f"  {column.name} {column.type}")
            schema_text += f"CREATE TABLE {table_name} (\\n" + ",\\n".join(columns) + "\\n);\\n\\n"
            
        return schema_text
    except Exception as e:
        return f"Error retrieving schema: {e}"

def execute_sql_query(query: str) -> str:
    """
    Executes a SELECT query on the database and returns the result string.
    """
    try:
        with engine.connect() as connection:
            result = connection.execute(text(query))
            rows = result.fetchall()
            
            if not rows:
                return "Query executed successfully, but returned no results."
            
            # Format results as a list of strings
            result_lines = []
            
            # Get column names
            col_names = list(result.keys())
            result_lines.append(" | ".join(col_names))
            result_lines.append("-" * 40)
            
            for row in rows:
                result_lines.append(" | ".join([str(val) for val in row]))
                
            return "\\n".join(result_lines)
            
    except SQLAlchemyError as e:
        return f"Database error executing query: {e}"
    except Exception as e:
        return f"Unknown error executing query: {e}"
