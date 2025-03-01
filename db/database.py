import os
import time
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

print(f"Usando banco de dados: {DATABASE_URL.split('@')[0]}@*****")

# Criar engine do SQLAlchemy com timeout aumentado
engine = create_engine(
    DATABASE_URL, 
    echo=False,
    pool_pre_ping=True,  # Verifica conexões antes de usar
    pool_recycle=3600,   # Recicla conexões a cada hora
    connect_args={"connect_timeout": 30}  # Timeout de conexão de 30 segundos
)

SessionFactory = sessionmaker(bind=engine)
Session = scoped_session(SessionFactory)

def init_db(max_retries=5, retry_delay=5):
    """Inicializa o banco de dados, criando as tabelas necessárias com retry"""
    retry_count = 0
    last_error = None
    
    while retry_count < max_retries:
        try:
            print(f"Tentativa {retry_count + 1} de inicializar o banco de dados...")
            
            # Criar banco de dados se não existir
            if not database_exists(engine.url):
                print("Banco de dados não existe, criando...")
                create_database(engine.url)
            
            # Criar tabelas
            print("Criando tabelas no banco de dados...")
            Base.metadata.create_all(engine)
            print("Banco de dados inicializado com sucesso!")
            
            # Testar conexão
            with get_db_session() as session:
                session.execute("SELECT 1")
                print("Conexão com o banco de dados testada com sucesso!")
            
            return True
            
        except Exception as e:
            last_error = str(e)
            print(f"Erro ao inicializar banco de dados: {e}")
            retry_count += 1
            
            if retry_count < max_retries:
                print(f"Aguardando {retry_delay} segundos antes de tentar novamente...")
                time.sleep(retry_delay)
                retry_delay *= 1.5  # Aumenta o tempo de espera entre tentativas
    
    print(f"Falha ao inicializar banco de dados após {max_retries} tentativas. Último erro: {last_error}")
    # Em produção, continuar mesmo com falha no banco
    if os.environ.get('RAILWAY_ENVIRONMENT'):
        print("Ambiente de produção detectado. Continuando mesmo com falha no banco...")
        return True
    return False

@contextmanager
def get_db_session():
    """Context manager para sessões do banco de dados com retry"""
    session = Session()
    try:
        yield session
        session.commit()
    except Exception as e:
        print(f"Erro na sessão do banco de dados: {e}")
        session.rollback()
        raise
    finally:
        session.close()