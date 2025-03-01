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

# Verificar se estamos usando SQLite ou PostgreSQL
is_sqlite = DATABASE_URL.startswith('sqlite:')

# Criar engine do SQLAlchemy com retry
max_retries = 5
retry_count = 0
retry_delay = 2

while retry_count < max_retries:
    try:
        # Configurar argumentos de conexão baseados no tipo de banco
        if is_sqlite:
            # SQLite não suporta connect_timeout
            engine = create_engine(
                DATABASE_URL, 
                echo=False,
                pool_pre_ping=True,
                pool_recycle=3600
            )
        else:
            # PostgreSQL suporta connect_timeout
            engine = create_engine(
                DATABASE_URL, 
                echo=False,
                pool_pre_ping=True,
                pool_recycle=3600,
                connect_args={"connect_timeout": 10}
            )

        # Testar conexão
        engine.connect()
        print("Conexão com o banco de dados estabelecida com sucesso!")
        break
    except Exception as e:
        retry_count += 1
        print(f"Erro ao conectar ao banco de dados (tentativa {retry_count}/{max_retries}): {e}")
        if retry_count < max_retries:
            print(f"Tentando novamente em {retry_delay} segundos...")
            time.sleep(retry_delay)
            retry_delay *= 1.5
        else:
            print("Falha ao conectar ao banco de dados após várias tentativas.")
            # Se já estiver usando SQLite, apenas aceite o erro e continue
            if is_sqlite:
                print("Usando SQLite com configurações padrão.")
                engine = create_engine(DATABASE_URL, echo=False)
            else:
                # Usar SQLite como fallback se PostgreSQL falhar
                print("Usando SQLite como fallback")
                DATABASE_URL = "sqlite:///./browser_agent_fallback.db"
                engine = create_engine(DATABASE_URL, echo=False)

SessionFactory = sessionmaker(bind=engine)
Session = scoped_session(SessionFactory)

def init_db():
    """Inicializa o banco de dados, criando as tabelas necessárias"""
    try:
        # Criar banco de dados se não existir (apenas PostgreSQL)
        if not is_sqlite and not database_exists(engine.url):
            print("Banco de dados não existe, criando...")
            create_database(engine.url)
        
        # Criar tabelas
        print("Criando tabelas no banco de dados...")
        Base.metadata.create_all(engine)
        print("Banco de dados inicializado com sucesso!")
        
        return True
    except Exception as e:
        print(f"Erro ao inicializar banco de dados: {e}")
        # Em modo de produção, continuar mesmo com erros
        if "RAILWAY_ENVIRONMENT" in os.environ:
            print("Ambiente de produção detectado. Continuando apesar do erro...")
            return True
        return False

@contextmanager
def get_db_session():
    """Context manager para sessões do banco de dados"""
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