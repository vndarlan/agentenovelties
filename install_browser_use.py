"""
Script para instalar dinamicamente o pacote browser-use quando necessário.
"""
import importlib
import subprocess
import sys
import os
import time

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

def try_import_or_install(module_name, package_name=None, max_retries=3):
    """Tenta importar um módulo, instalando-o se necessário"""
    if package_name is None:
        package_name = module_name
    
    for attempt in range(max_retries):
        try:
            importlib.import_module(module_name)
            print(f"Módulo {module_name} já está disponível")
            return True
        except ImportError:
            print(f"Módulo {module_name} não encontrado, tentando instalar (tentativa {attempt+1}/{max_retries})...")
            if install_package(package_name):
                try:
                    importlib.import_module(module_name)
                    print(f"Módulo {module_name} importado com sucesso após instalação")
                    return True
                except ImportError:
                    print(f"Falha ao importar {module_name} mesmo após instalação")
            
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Backoff exponencial
                print(f"Aguardando {wait_time} segundos antes de tentar novamente...")
                time.sleep(wait_time)
    
    return False

def setup_browser_use():
    """Instala o browser-use e suas dependências"""
    # Tentar instalar browser-use
    return try_import_or_install("browser_use", "browser-use==0.0.41")

if __name__ == "__main__":
    setup_browser_use()