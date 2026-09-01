from .database import Base, SessionLocal, engine
from .services import check_all
def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        for product_id, result in check_all(db): print(f"{product_id}: {result}")
    finally: db.close()
if __name__ == "__main__": main()
