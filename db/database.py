import os
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import database_exists, create_database
from db.models import Base

# Obter URL do banco de dados da variável de ambiente ou usar SQLite por padrão
DATABASE_URL = os.environ.get('DATABASE_URL')

# Ajustar URL se for PostgreSQL do Heroku/Railway (que começa com postgres://)
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
elif not DATABASE_URL:
    # Usar SQLite para desenvolvimento local
    DATABASE_URL = "sqlite:///./browser_agent.db"

# Criar engine do SQLAlchemy
engine = create_engine(DATABASE_URL, echo=False)
SessionFactory = sessionmaker(bind=engine)
Session = scoped_session(SessionFactory)

def init_db():
    """Inicializa o banco de dados, criando as tabelas necessárias"""
    # Criar banco de dados se não existir
    if not database_exists(engine.url):
        create_database(engine.url)
    
    # Criar tabelas
    Base.metadata.create_all(engine)
    
    return True

@contextmanager
def get_db_session():
    """Context manager para sessões do banco de dados"""
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()