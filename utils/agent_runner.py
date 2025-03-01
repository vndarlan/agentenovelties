import os
import json
import asyncio
from datetime import datetime
import tempfile
from pathlib import Path

# Importações do Browser Use
from browser_use import Agent, Browser, BrowserConfig
from browser_use.browser.context import BrowserContextConfig

def get_llm_instance(provider, model, api_key, endpoint=None):
    """Retorna uma instância do LLM configurado"""
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
        
        # Configurar o navegador
        context_config = BrowserContextConfig(
            browser_window_size={
                'width': browser_config['browser_window_width'], 
                'height': browser_config['browser_window_height']
            },
            highlight_elements=browser_config['highlight_elements'],
        )
        
        browser_conf = BrowserConfig(
            headless=browser_config['headless'],
            disable_security=browser_config['disable_security'],
            new_context_config=context_config,
            chrome_instance_path=browser_config['chrome_instance_path'] if browser_config['chrome_instance_path'] else None
        )
        
        # Para ambientes de servidor (Railway), forçar o modo headless
        if os.environ.get('RAILWAY_ENVIRONMENT'):
            browser_conf.headless = True
        
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