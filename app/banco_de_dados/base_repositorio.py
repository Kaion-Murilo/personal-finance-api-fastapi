from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from typing import TypeVar, Generic, List, Optional

# T representa o model SQLAlchemy que o repositório vai gerenciar
# Ex: BaseRepositorio[Category], BaseRepositorio[Transaction]
T = TypeVar('T')


class BaseRepositorio(ABC, Generic[T]):
    """
    Contrato base para todos os repositórios da aplicação.

    Define os métodos obrigatórios que qualquer repositório deve implementar.
    Garante consistência entre os repositórios e facilita a troca de
    implementação sem afetar o Service Layer.

    Padrão: Repository Pattern
    Uso: class CategoryRepositorio(BaseRepositorio[Category])
    """

    @staticmethod
    @abstractmethod
    def listar(db: Session) -> List[T]:
        """Retorna todos os registros da entidade."""
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def buscar_por_id(db: Session, id: int) -> Optional[T]:
        """Busca um registro pelo id. Retorna None se não encontrado."""
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def criar(db: Session, **kwargs) -> T:
        """Cria e persiste um novo registro. Retorna o objeto criado com id."""
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def editar(db: Session, id: int, **kwargs) -> Optional[T]:
        """
        Atualiza um registro existente.
        Retorna o objeto atualizado ou None se não encontrado.
        Não lança exceção — a checagem de existência fica no Service Layer.
        """
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def deletar(db: Session, id: int) -> Optional[T]:
        """
        Remove um registro do banco.
        Retorna o objeto deletado ou None se não encontrado.
        """
        raise NotImplementedError