from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://postgres:admin@localhost:5050/personal_finance"

engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("Conexão OK:", result.scalar())
except Exception as e:
    print("Erro na conexão:", e)