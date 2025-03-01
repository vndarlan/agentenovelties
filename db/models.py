from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class Task(Base):
    """Modelo para representar uma tarefa de automação"""
    __tablename__ = 'tasks'

    id = Column(String(36), primary_key=True)
    task = Column(Text, nullable=False)
    status = Column(String(20), default='created')  # created, running, finished, failed, stopped
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    finished_at = Column(DateTime, nullable=True)
    llm_provider = Column(String(50), nullable=False)
    llm_model = Column(String(100), nullable=False)
    output = Column(Text, nullable=True)

    def __repr__(self):
        return f"<Task(id='{self.id}', status='{self.status}')>"

class TaskHistory(Base):
    """Modelo para armazenar o histórico detalhado de uma tarefa"""
    __tablename__ = 'task_history'

    task_id = Column(String(36), ForeignKey('tasks.id'), primary_key=True)
    steps = Column(Text, nullable=True)  # JSON string com os passos de execução
    urls = Column(Text, nullable=True)   # JSON string com URLs visitadas
    screenshots = Column(Text, nullable=True)  # JSON string com caminhos para screenshots
    errors = Column(Text, nullable=True)  # JSON string com erros encontrados

    def __repr__(self):
        return f"<TaskHistory(task_id='{self.task_id}')>"

class ApiKey(Base):
    """Modelo para armazenar chaves de API e configurações"""
    __tablename__ = 'api_keys'

    provider = Column(String(50), primary_key=True)  # openai, anthropic, azure, gemini, deepseek, browser_config, etc.
    api_key = Column(Text, nullable=False)  # Para o provider 'browser_config', isso armazena um JSON com as configurações

    def __repr__(self):
        return f"<ApiKey(provider='{self.provider}')>"