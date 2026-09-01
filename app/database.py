from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from .config import DATABASE_URL
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
class Base(DeclarativeBase): pass

def ensure_schema():
    """Add small backwards-compatible columns for existing local databases."""
    Base.metadata.create_all(bind=engine)
    columns = {column["name"] for column in inspect(engine).get_columns("products")}
    if "alert_email" not in columns:
        with engine.begin() as connection:
            connection.execute(text("ALTER TABLE products ADD COLUMN alert_email VARCHAR(320)"))
    if "alert_sent_at" not in columns:
        with engine.begin() as connection:
            connection.execute(text("ALTER TABLE products ADD COLUMN alert_sent_at DATETIME"))
def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()
