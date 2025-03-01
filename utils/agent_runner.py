import os
import json
import asyncio
from datetime import datetime
import tempfile
from pathlib import Path

# Importar instaladores dinâmicos
try:
    from install_langchain import setup_langchain
    from install_browser_use import setup_browser_use
except ImportError:
    # Se os instaladores não estiverem disponíveis, criar funções vazias
    def setup_langchain():
        return True
    def setup_browser_use():
        return True

# Verificar e instalar dependências
setup_langchain()
setup_browser_use()

# Tentar importações após garantir que as dependências estão instaladas
try:
    # Importações do Browser Use
    from browser_use import Agent, Browser, BrowserConfig
    from browser_use.browser.context import BrowserContextConfig
    from utils.browser_config import get_browser_config
except ImportError as e:
    print(f"Erro ao importar pacotes do browser_use: {e}")
    # Definir funções de fallback para evitar erros fatais
    class Browser:
        def __init__(self, config):
            self.config = config
        async def close(self):
            pass
    
    class Agent:
        def __init__(self, task, llm, browser):
            self.task = task
            self.llm = llm
            self.browser = browser
        async def run(self):
            return {
                'status': 'failed',
                'errors': [f"Não foi possível carregar as dependências do browser_use: {e}"],
                'final_result': lambda: "Falha ao carregar dependências necessárias",
                'model_actions': lambda: [],
                'urls': lambda: [],
                'screenshots': lambda: [],
                'extracted_content': lambda: [],
                'is_done': lambda: False,
                'has_errors': lambda: True
            }

def get_llm_instance(provider, model, api_key, endpoint=None):
    """Retorna uma instância do LLM configurado"""
    try:
        if provider == 'openai':
            from langchain_openai import ChatOpenAI
            os.environ["OPENAI_API_KEY"] = api_key
            return ChatOpenAI(model=model, temperature=0.0)
            
        elif provider == 'anthropic':
            from langchain_anthropic import ChatAnthropic
            os.environ["ANTHROPIC_API_KEY"] = api_key
            return ChatAnthropic(model_name=model, temperature=0.0)
            
        elif provider == 'azure':
            from langchain_openai import AzureChatOpenAI
            from pydantic import SecretStr
            return AzureChatOpenAI(
                model=model,
                api_version='2024-10-21',
                azure_endpoint=endpoint,
                api_key=SecretStr(api_key),
            )
            
        elif provider == 'gemini':
            from langchain_google_genai import ChatGoogleGenerativeAI
            from pydantic import SecretStr
            os.environ["GEMINI_API_KEY"] = api_key
            return ChatGoogleGenerativeAI(model=model, api_key=SecretStr(api_key))
            
        elif provider == 'deepseek':
            from langchain_openai import ChatOpenAI
            from pydantic import SecretStr
            return ChatOpenAI(base_url='https://api.deepseek.com/v1', model=model, api_key=SecretStr(api_key))
            
        elif provider == 'ollama':
            from langchain_ollama import ChatOllama
            return ChatOllama(model=model, num_ctx=32000)
        
        else:
            # Por padrão, usar OpenAI
            from langchain_openai import ChatOpenAI
            os.environ["OPENAI_API_KEY"] = api_key
            return ChatOpenAI(model=model, temperature=0.0)
    except Exception as e:
        print(f"Erro ao criar instância LLM ({provider}/{model}): {e}")
        # Retornar um objeto dummy que apenas registra o erro
        class DummyLLM:
            def __call__(self, *args, **kwargs):
                return f"Erro: {e}"
        return DummyLLM()

async def run_agent_task(task_id, task_instructions, llm, browser_config, save_path=None):
    """Executa uma tarefa de agente de forma assíncrona"""
    try:
        # Criar diretório para armazenar screenshots
        screenshot_dir = Path(tempfile.gettempdir()) / "browser_agent_screenshots" / task_id
        screenshot_dir.mkdir(parents=True, exist_ok=True)
        
        # Configurar o modelo LLM
        llm_instance = get_llm_instance(
            llm['provider'], 
            llm['model'], 
            llm['api_key'], 
            llm.get('endpoint')
        )
        
        # Configurar o navegador usando a configuração otimizada
        try:
            from utils.browser_config import get_browser_config
            browser_conf = get_browser_config(browser_config)
        except ImportError:
            # Configuração de fallback se não puder importar
            browser_conf = BrowserConfig(
                headless=True,
                disable_security=True
            )
        
        browser = Browser(config=browser_conf)
        
        # Configurar e executar o agente
        agent = Agent(
            task=task_instructions,
            llm=llm_instance,
            browser=browser,
        )
        
        # Executar o agente e obter o histórico
        history = await agent.run()
        
        # Fechar o navegador
        await browser.close()
        
        # Copiar screenshots para o diretório temporário se existirem
        screenshot_paths = []
        for src_path in history.screenshots():
            if os.path.exists(src_path):
                # Criar nome de arquivo com base no original
                screenshot_filename = f"{task_id}_{os.path.basename(src_path)}"
                dst_path = screenshot_dir / screenshot_filename
                
                # Copiar o arquivo se possível
                try:
                    import shutil
                    shutil.copy2(src_path, dst_path)
                    screenshot_paths.append(str(dst_path))
                except Exception as e:
                    print(f"Erro ao copiar screenshot: {e}")
                    screenshot_paths.append(src_path)
            else:
                screenshot_paths.append(src_path)
        
        # Preparar resultado
        result = {
            'id': task_id,
            'task': task_instructions,
            'status': 'finished',
            'created_at': datetime.now().isoformat(),
            'finished_at': datetime.now().isoformat(),
            'output': history.final_result(),
            'steps': [
                {
                    'id': f"step-{i}",
                    'step': i,
                    'evaluation_previous_goal': str(action.get('thought', '')),
                    'next_goal': str(action.get('action', {}).get('name', ''))
                }
                for i, action in enumerate(history.model_actions())
            ],
            'urls': history.urls(),
            'screenshots': screenshot_paths,
            'extracted_content': history.extracted_content(),
            'errors': history.errors(),
            'is_done': history.is_done(),
            'has_errors': history.has_errors(),
        }
        
        return result
        
    except Exception as e:
        # Em caso de erro, retornar informações de erro
        import traceback
        error_details = traceback.format_exc()
        
        return {
            'id': task_id,
            'task': task_instructions,
            'status': 'failed',
            'created_at': datetime.now().isoformat(),
            'finished_at': datetime.now().isoformat(),
            'output': f"Erro: {str(e)}",
            'steps': [],
            'errors': [str(e), error_details],
            'has_errors': True,
            'is_done': False,
        }