"""
Script para verificar a disponibilidade do pacote browser-use e fornecer funcionalidade de fallback.
"""
import importlib
import subprocess
import sys
import os
import time

def check_package_installed(package_name):
    """Verifica se um pacote está instalado"""
    try:
        importlib.import_module(package_name)
        return True
    except ImportError:
        return False

def create_dummy_browser_use():
    """
    Cria módulos e classes dummy para browser-use quando o pacote não está disponível.
    Isso permite que o código principal continue funcionando mesmo sem o pacote real.
    """
    print("Criando funcionalidade de fallback para browser-use...")
    
    # Criar diretório para módulo dummy se não existir
    os.makedirs('browser_use_fallback', exist_ok=True)
    
    # Criar arquivo __init__.py para o módulo dummy
    with open('browser_use_fallback/__init__.py', 'w') as f:
        f.write("""
# Fallback module for browser-use
from .browser import Browser, BrowserConfig
from .agent import Agent

__all__ = ['Browser', 'BrowserConfig', 'Agent']
""")
    
    # Criar arquivo browser.py com classes dummy
    with open('browser_use_fallback/browser.py', 'w') as f:
        f.write("""
# Dummy browser classes
class BrowserContextConfig:
    def __init__(self, browser_window_size=None, highlight_elements=False):
        self.browser_window_size = browser_window_size or {'width': 1280, 'height': 800}
        self.highlight_elements = highlight_elements

class BrowserConfig:
    def __init__(self, headless=True, disable_security=False, new_context_config=None, 
                 chrome_instance_path=None, extra_chromium_args=None):
        self.headless = headless
        self.disable_security = disable_security
        self.new_context_config = new_context_config
        self.chrome_instance_path = chrome_instance_path
        self.extra_chromium_args = extra_chromium_args or []

class Browser:
    def __init__(self, config):
        self.config = config
        print("Dummy Browser initialized with config:", config.__dict__)
    
    async def close(self):
        print("Dummy Browser closed")
""")
    
    # Criar arquivo agent.py com classe Agent dummy
    with open('browser_use_fallback/agent.py', 'w') as f:
        f.write("""
# Dummy Agent class
class AgentHistory:
    def __init__(self):
        self._status = "finished"
        
    def final_result(self):
        return "Dummy agent couldn't execute the task (browser-use not available)"
        
    def model_actions(self):
        return []
        
    def urls(self):
        return []
        
    def screenshots(self):
        return []
        
    def extracted_content(self):
        return []
        
    def is_done(self):
        return True
        
    def has_errors(self):
        return True
        
    def errors(self):
        return ["browser-use package not available"]

class Agent:
    def __init__(self, task, llm, browser):
        self.task = task
        self.llm = llm
        self.browser = browser
        print(f"Dummy Agent initialized with task: {task[:50]}...")
        
    async def run(self):
        print("Dummy Agent run method called")
        return AgentHistory()
""")
    
    # Adicionar diretório ao path do Python
    sys.path.insert(0, os.getcwd())
    
    print("Módulo de fallback criado com sucesso")
    return True

def setup_browser_use():
    """Verifica se browser-use está disponível e cria um fallback se necessário"""
    # Tentar importar browser-use
    try:
        import browser_use
        print("O pacote browser-use já está instalado e disponível")
        return True
    except ImportError:
        print("O pacote browser-use não está disponível")
        
        # Tentar instalar o pacote (isso provavelmente falhará, mas vamos tentar)
        try:
            print("Tentando instalar browser-use...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "browser-use"])
            print("browser-use instalado com sucesso!")
            
            # Verificar se a instalação funcionou
            try:
                import browser_use
                print("Importação de browser-use bem-sucedida após instalação")
                return True
            except ImportError:
                print("Falha ao importar browser-use mesmo após tentativa de instalação")
        except Exception as e:
            print(f"Erro ao tentar instalar browser-use: {e}")
        
        # Se não conseguimos instalar, criar fallback
        try:
            success = create_dummy_browser_use()
            if success:
                # Adicionar alias para o módulo
                sys.modules['browser_use'] = importlib.import_module('browser_use_fallback')
                from browser_use_fallback.browser import BrowserContextConfig
                sys.modules['browser_use.browser.context'] = type('module', (), {'BrowserContextConfig': BrowserContextConfig})
                print("Módulo de fallback criado e configurado com sucesso")
                return True
        except Exception as e:
            print(f"Erro ao criar módulo de fallback: {e}")
        
        return False

if __name__ == "__main__":
    setup_browser_use()