from .database import SessionLocal, ensure_schema
from .services import check_all
def main():
    ensure_schema()
    db = SessionLocal()
    try:
        for product_id, result in check_all(db): print(f"{product_id}: {result}")
    finally: db.close()
if __name__ == "__main__": main()
