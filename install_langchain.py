"""
Script para instalar dinamicamente os pacotes do LangChain quando necessário.
"""
import importlib
import subprocess
import sys
import os

def install_package(package):
    """Instala um pacote Python usando pip"""
    print(f"Instalando {package}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"Instalação de {package} concluída com sucesso!")
        return True
    except Exception as e:
        print(f"Erro ao instalar {package}: {e}")
        return False

def try_import_or_install(module_name, package_name=None):
    """Tenta importar um módulo, instalando-o se necessário"""
    if package_name is None:
        package_name = module_name
    
    try:
        importlib.import_module(module_name)
        print(f"Módulo {module_name} já está disponível")
        return True
    except ImportError:
        print(f"Módulo {module_name} não encontrado, tentando instalar...")
        if install_package(package_name):
            try:
                importlib.import_module(module_name)
                print(f"Módulo {module_name} importado com sucesso após instalação")
                return True
            except ImportError:
                print(f"Falha ao importar {module_name} mesmo após instalação")
                return False
        return False

def setup_langchain():
    """Configura pacotes do LangChain conforme necessário"""
    # Lista de pacotes para instalar sob demanda
    core_packages = [
        ("langchain_core", "langchain-core>=0.0.9"),
    ]
    
    # Pacotes adicionais baseados em quais LLMs são usados
    llm_packages = [
        ("langchain_openai", "langchain-openai>=0.0.2"),
        ("langchain_anthropic", "langchain-anthropic>=0.0.7"),
        ("langchain_google_genai", "langchain-google-genai>=0.0.3"),
        ("langchain_ollama", "langchain-ollama>=0.1.0")  # Corrigido para usar versão disponível
    ]
    
    # Instalar pacotes core
    for module_name, package_name in core_packages:
        try_import_or_install(module_name, package_name)
    
    # Instalar pacotes de LLM
    for module_name, package_name in llm_packages:
        try_import_or_install(module_name, package_name)
    
    return True

if __name__ == "__main__":
    setup_langchain()