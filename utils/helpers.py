import uuid
from datetime import datetime

def generate_unique_id():
    """Gera um ID único para a tarefa"""
    return str(uuid.uuid4())

def format_datetime(dt):
    """Formata datetime para exibição"""
    if not dt:
        return "N/A"
    
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
        except:
            return dt
    
    return dt.strftime('%d/%m/%Y %H:%M:%S')

def get_status_color(status):
    """Retorna cor associada ao status da tarefa"""
    colors = {
        'created': 'blue',
        'running': 'orange',
        'finished': 'green',
        'stopped': 'red',
        'paused': 'yellow',
        'failed': 'darkred'
    }
    return colors.get(status, 'gray')

def get_llm_models(provider):
    """Retorna os modelos disponíveis para o provedor selecionado"""
    models = {
        'openai': ['gpt-4o', 'gpt-4o-mini', 'gpt-4-turbo', 'gpt-3.5-turbo'],
        'anthropic': ['claude-3-5-sonnet-20240620', 'claude-3-opus-20240229', 'claude-3-sonnet-20240229', 'claude-3-haiku-20240307'],
        'azure': ['gpt-4o', 'gpt-4-turbo', 'gpt-3.5-turbo'],
        'gemini': ['gemini-2.0-flash-exp', 'gemini-1.5-pro-001', 'gemini-1.5-flash-001'],
        'deepseek': ['deepseek-chat', 'deepseek-reasoner'],
        'ollama': ['qwen2.5', 'llama3', 'mistral']
    }
    return models.get(provider, ['modelo não disponível'])