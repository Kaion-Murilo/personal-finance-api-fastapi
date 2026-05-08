import os
from sqlalchemy import create_engine, text

def criar_banco():
    senha = os.getenv("OSTGRES_PASSWORD")

    engine = create_engine(
        f"postgresql://postgres:admin@localhost:5432/personal_finance"
    )