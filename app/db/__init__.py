from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from config import Config
# import sys
# import os


# def resource_path(relative_path):
#     """ Get absolute path to resource, works for dev and for PyInstaller """
#     try:
#         # PyInstaller creates a temp folder and stores path in _MEIPASS
#         base_path = sys._MEIPASS
#     except Exception:
#         base_path = os.path.abspath(".")

#     return os.path.join(base_path, relative_path)

# db_path = resource_path('budgeter.db')

# engine = create_engine(f"sqlite:///{db_path}")

engine = create_engine(Config.DATABASE_URL, echo=True, future=True)


SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
db_session = SessionLocal()

Base = declarative_base()


