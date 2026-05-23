from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings


DATABASE_URL = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"

engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=11,
    pool_pre_ping=True,
    pool_recycle=900,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

def get_db():
    # This function is a dependency that can be used in FastAPI routes to get a database session. It ensures that the session is properly closed after use.
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def run_query(query: str):
    """ 
        This function is a simple wrapper around SQLAlchemy's connection execution to run raw SQL queries.
        param query: The SQL query to be executed.
    """
    with engine.connect() as connection:
        result = connection.execute(text(query))
        # Max 60 rows to prevent overwhelming the agent with too much data. Adjust as needed.
        return result.fetchmany(60)
