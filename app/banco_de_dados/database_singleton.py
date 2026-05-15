from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

# override=False garante que variáveis já injetadas pelo Docker não sejam
# sobrescritas pelo .env — permite o mesmo código rodar local e em container
load_dotenv(override=False)

# Base compartilhada por todos os models — deve ser importada de cá
# para que o create_all encontre todas as tabelas registradas
Base = declarative_base()


class DatabaseSingleton:
    """
    Gerencia a conexão com o banco de dados usando o padrão Singleton.

    Garante que o engine SQLAlchemy seja criado apenas uma vez durante
    toda a vida da aplicação, evitando múltiplas conexões desnecessárias
    e inconsistências de configuração.

    Padrão: Singleton
    Uso: db = DatabaseSingleton()  — sempre retorna a mesma instância
    """

    _instance = None
    _engine = None
    _session_factory = None

    def __new__(cls):
        """
        Intercepta a criação da instância.
        Se já existir uma instância, retorna ela — nunca cria duas.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_db()
        return cls._instance

    def _init_db(self):
        """
        Inicializa o engine e a session factory.
        Chamado apenas uma vez — na primeira instanciação.

        O fallback da DATABASE_URL aponta para localhost para
        funcionar sem Docker durante o desenvolvimento local.
        """
        DATABASE_URL = os.getenv(
            "DATABASE_URL",
            "postgresql://postgres:postgres@localhost:5432/personal_finance"
        )

        # echo=True loga todas as queries SQL no terminal — útil para debug
        # desativar em produção para não poluir os logs
        self._engine = create_engine(DATABASE_URL, echo=True, future=True)

        # autocommit=False exige commit explícito — evita gravações acidentais
        # autoflush=False evita queries automáticas antes do commit
        self._session_factory = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self._engine
        )
        print("Database engine criado — instância Singleton inicializada.")

    @property
    def engine(self):
        """Engine SQLAlchemy — usado para create_all e migrações."""
        return self._engine

    @property
    def session_factory(self):
        """Factory de sessões — usado para abrir conexões com o banco."""
        return self._session_factory

    def get_session(self):
        """
        Gerador de sessão para uso com Depends() do FastAPI.
        Garante que a sessão seja fechada ao final de cada requisição,
        mesmo em caso de erro.
        """
        db = self._session_factory()
        try:
            yield db
        finally:
            db.close()