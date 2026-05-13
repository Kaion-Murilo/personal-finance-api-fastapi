from app.banco_de_dados.database import SessionLocal
from app.models.user import UserTable
from app.models.category import Category
from app.models.transactions import Transaction
from app.auth.auth import gerar_hash_senha
from datetime import date

def seed():
    db = SessionLocal()

    # verifica se já tem dados
    if db.query(UserTable).first():
        print("Banco já tem dados, seed ignorado.")
        db.close()
        return

    print("Criando dados iniciais...")

    # ── Usuários ──────────────────────────────────────
    usuario1 = UserTable(
        nome="Admin",
        email="admin@finance.com",
        password_hash=gerar_hash_senha("admin123")
    )
    usuario2 = UserTable(
        nome="Maria Silva",
        email="maria@finance.com",
        password_hash=gerar_hash_senha("maria123")
    )
    db.add_all([usuario1, usuario2])
    db.commit()
    db.refresh(usuario1)
    db.refresh(usuario2)

    # ── Categorias ────────────────────────────────────
    categorias_u1 = [
        Category(name="Salário", description="Salário mensal", type="income", user_id=usuario1.id),
        Category(name="Freelance", description="Trabalhos extras", type="income", user_id=usuario1.id),
        Category(name="Alimentação", description="Mercado e restaurantes", type="expense", user_id=usuario1.id),
        Category(name="Transporte", description="Uber, gasolina, ônibus", type="expense", user_id=usuario1.id),
        Category(name="Moradia", description="Aluguel e contas", type="expense", user_id=usuario1.id),
    ]
    categorias_u2 = [
        Category(name="Salário", description="Salário mensal", type="income", user_id=usuario2.id),
        Category(name="Alimentação", description="Mercado e restaurantes", type="expense", user_id=usuario2.id),
        Category(name="Lazer", description="Cinema, viagens", type="expense", user_id=usuario2.id),
    ]
    db.add_all(categorias_u1 + categorias_u2)
    db.commit()
    for cat in categorias_u1 + categorias_u2:
        db.refresh(cat)

    # ── Transações ────────────────────────────────────
    transacoes = [
        Transaction(title="Salário Março", amount=5000, date=date(2026, 3, 5), user_id=usuario1.id, category_id=categorias_u1[0].id),
        Transaction(title="Freelance site", amount=1500, date=date(2026, 3, 10), user_id=usuario1.id, category_id=categorias_u1[1].id),
        Transaction(title="Mercado", amount=450, date=date(2026, 3, 12), user_id=usuario1.id, category_id=categorias_u1[2].id),
        Transaction(title="Uber", amount=120, date=date(2026, 3, 15), user_id=usuario1.id, category_id=categorias_u1[3].id),
        Transaction(title="Aluguel", amount=1800, date=date(2026, 3, 1), user_id=usuario1.id, category_id=categorias_u1[4].id),
        Transaction(title="Salário Abril", amount=5000, date=date(2026, 4, 5), user_id=usuario1.id, category_id=categorias_u1[0].id),
        Transaction(title="Restaurante", amount=200, date=date(2026, 4, 8), user_id=usuario1.id, category_id=categorias_u1[2].id),
        Transaction(title="Gasolina", amount=300, date=date(2026, 4, 10), user_id=usuario1.id, category_id=categorias_u1[3].id),

        Transaction(title="Salário Março", amount=3500, date=date(2026, 3, 5), user_id=usuario2.id, category_id=categorias_u2[0].id),
        Transaction(title="Mercado", amount=380, date=date(2026, 3, 14), user_id=usuario2.id, category_id=categorias_u2[1].id),
        Transaction(title="Cinema", amount=80, date=date(2026, 3, 20), user_id=usuario2.id, category_id=categorias_u2[2].id),
        Transaction(title="Salário Abril", amount=3500, date=date(2026, 4, 5), user_id=usuario2.id, category_id=categorias_u2[0].id),
    ]
    db.add_all(transacoes)
    db.commit()

    print("Seed concluído!")
    print("Usuário 1: admin@finance.com / admin123")
    print("Usuário 2: maria@finance.com / maria123")
    db.close()

if __name__ == "__main__":
    seed()