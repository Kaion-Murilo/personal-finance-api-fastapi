from sqlalchemy.orm import Session
from sqlalchemy import extract
from app.models.transactions import Transaction
from app.banco_de_dados.base_repositorio import BaseRepositorio
from datetime import date
from typing import List, Optional


class TransactionRepositorio(BaseRepositorio[Transaction]):
    """
    Repositório de transações — acesso ao banco para operações CRUD e relatórios.
    Todas as queries filtram por user_id para garantir isolamento entre usuários.
    """

    @staticmethod
    def listar(db: Session) -> List[Transaction]:
        """Retorna todas as transações — uso interno/administrativo."""
        return db.query(Transaction).all()

    @staticmethod
    def buscar_por_id(db: Session, id: int) -> Optional[Transaction]:
        """Busca uma transação pelo id sem filtrar por usuário."""
        return db.query(Transaction).filter(Transaction.id == id).first()

    @staticmethod
    def listar_por_usuario(
        db: Session,
        user_id: int,
        data_inicio: Optional[date] = None,
        data_fim: Optional[date] = None,
        category_id: Optional[int] = None
    ) -> List[Transaction]:
        """
        Retorna transações do usuário com filtros opcionais.
        Ordenadas da mais recente para a mais antiga.
        Todos os filtros são cumulativos — podem ser combinados livremente.
        """
        query = db.query(Transaction).filter(Transaction.user_id == user_id)

        if data_inicio:
            query = query.filter(Transaction.date >= data_inicio)
        if data_fim:
            query = query.filter(Transaction.date <= data_fim)
        if category_id:
            query = query.filter(Transaction.category_id == category_id)

        return query.order_by(Transaction.date.desc()).all()

    @staticmethod
    def criar(
        db: Session,
        title: str,
        amount: float,
        date: date,
        user_id: int,
        category_id: int
    ) -> Transaction:
        """
        Cria e persiste uma nova transação.
        O db.refresh garante que o objeto retornado tem o id gerado pelo banco.
        """
        nova = Transaction(
            title=title,
            amount=amount,
            date=date,
            user_id=user_id,
            category_id=category_id
        )
        db.add(nova)
        db.commit()
        db.refresh(nova)
        return nova

    @staticmethod
    def editar(
        db: Session,
        id: int,
        title: str,
        amount: float,
        date: date,
        user_id: int,
        category_id: int
    ) -> Optional[Transaction]:
        """
        Atualiza uma transação — filtra por id E user_id.
        Se não pertencer ao usuário, retorna None sem lançar erro.
        A checagem de permissão fica no Service Layer.
        """
        t = db.query(Transaction).filter(
            Transaction.id == id,
            Transaction.user_id == user_id
        ).first()

        if t:
            t.title = title
            t.amount = amount
            t.date = date
            t.category_id = category_id
            db.commit()
            db.refresh(t)

        return t

    @staticmethod
    def deletar(db: Session, id: int, user_id: int = None) -> Optional[Transaction]:
        """
        Remove uma transação do banco.
        user_id é opcional — quando informado, garante que o usuário só
        deleta suas próprias transações. Sem user_id, uso administrativo.
        """
        query = db.query(Transaction).filter(Transaction.id == id)

        # restringe ao dono quando user_id for fornecido
        if user_id:
            query = query.filter(Transaction.user_id == user_id)

        t = query.first()

        if t:
            db.delete(t)
            db.commit()

        return t

    @staticmethod
    def resumo(
        db: Session,
        user_id: int,
        data_inicio: Optional[date] = None,
        data_fim: Optional[date] = None
    ) -> dict:
        """
        Calcula o resumo financeiro do usuário no período informado.
        Usa o relacionamento t.category.type para classificar cada transação.
        Se nenhum período for informado, considera todas as transações.
        """
        query = db.query(Transaction).filter(Transaction.user_id == user_id)

        if data_inicio:
            query = query.filter(Transaction.date >= data_inicio)
        if data_fim:
            query = query.filter(Transaction.date <= data_fim)

        transacoes = query.all()

        receitas = sum(float(t.amount) for t in transacoes if t.category.type == "income") if transacoes else 0
        despesas = sum(float(t.amount) for t in transacoes if t.category.type == "expense") if transacoes else 0

        return {
            "total_receitas": receitas,
            "total_despesas": despesas,
            "saldo": receitas - despesas,
            "total_transacoes": len(transacoes)
        }

    @staticmethod
    def resumo_mensal(db: Session, user_id: int, ano: int) -> List[dict]:
        """
        Retorna receitas, despesas e saldo para cada mês do ano informado.
        Sempre retorna 12 entradas — meses sem transações terão valores zerados.
        Usado no gráfico de barras do dashboard.
        """
        resultado = []

        for mes in range(1, 13):
            transacoes = db.query(Transaction).filter(
                Transaction.user_id == user_id,
                extract('year', Transaction.date) == ano,
                extract('month', Transaction.date) == mes
            ).all()

            receitas = sum(float(t.amount) for t in transacoes if t.category.type == "income")
            despesas = sum(float(t.amount) for t in transacoes if t.category.type == "expense")

            resultado.append({
                "mes": mes,
                "receitas": receitas,
                "despesas": despesas,
                "saldo": receitas - despesas
            })

        return resultado

    @staticmethod
    def resumo_por_categoria(
        db: Session,
        user_id: int,
        data_inicio: Optional[date] = None,
        data_fim: Optional[date] = None
    ) -> List[dict]:
        """
        Agrupa transações por categoria calculando total e quantidade.
        Útil para relatórios de onde o usuário mais gasta ou recebe.
        Retorna lista ordenada pela ordem de aparição nas transações.
        """
        query = db.query(Transaction).filter(Transaction.user_id == user_id)

        if data_inicio:
            query = query.filter(Transaction.date >= data_inicio)
        if data_fim:
            query = query.filter(Transaction.date <= data_fim)

        transacoes = query.all()

        # dict temporário para acumular totais por categoria
        # chave é o nome da categoria para evitar duplicatas
        categorias: dict = {}

        for t in transacoes:
            nome = t.category.name
            if nome not in categorias:
                categorias[nome] = {
                    "categoria": nome,
                    "tipo": t.category.type,
                    "total": 0,
                    "quantidade": 0
                }
            categorias[nome]["total"] += float(t.amount)
            categorias[nome]["quantidade"] += 1

        return list(categorias.values())