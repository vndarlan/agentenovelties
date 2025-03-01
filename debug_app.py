import streamlit as st
import time
import os

# Configuração básica do Streamlit
st.set_page_config(page_title="Diagnóstico", page_icon="🔍")

def main():
    """Aplicação de diagnóstico para identificar problemas"""
    st.title("🔍 Diagnóstico da Aplicação")
    
    st.write("### Verificando ambiente")
    
    # Verificar pacotes instalados
    st.write("#### Pacotes instalados:")
    try:
        import pandas
        st.success("✅ pandas")
    except ImportError:
        st.error("❌ pandas")

    try:
        import sqlalchemy
        st.success("✅ sqlalchemy")
    except ImportError:
        st.error("❌ sqlalchemy")
        
    try:
        import playwright
        st.success("✅ playwright")
    except ImportError:
        st.error("❌ playwright")
    
    # Verificar variáveis de ambiente
    st.write("#### Variáveis de ambiente:")
    env_vars = ["PORT", "DATABASE_URL", "RAILWAY_ENVIRONMENT", "RAILWAY_PUBLIC_DOMAIN"]
    for var in env_vars:
        value = os.environ.get(var)
        if value:
            st.success(f"✅ {var} = {value[:10]}{'...' if len(value) > 10 else ''}")
        else:
            st.warning(f"⚠️ {var} não definido")
    
    # Verificar sistema de arquivos
    st.write("#### Sistema de arquivos:")
    files = ["app.py", "requirements.txt", ".streamlit/config.toml"]
    for file in files:
        if os.path.exists(file):
            st.success(f"✅ {file} existe")
        else:
            st.error(f"❌ {file} não encontrado")
    
    # Criar componentes UI básicos para testar funcionamento
    st.write("### Teste de componentes Streamlit")
    
    st.write("#### Teste de texto básico")
    st.write("Este é um texto simples para verificar a renderização básica.")
    
    st.write("#### Teste de entrada de dados")
    test_input = st.text_input("Digite algo aqui")
    if test_input:
        st.write(f"Você digitou: {test_input}")
    
    st.write("#### Teste de botão")
    if st.button("Clique aqui"):
        st.success("Botão funcionando corretamente!")
    
    st.write("#### Teste de seleção")
    option = st.selectbox("Selecione uma opção", ["Opção 1", "Opção 2", "Opção 3"])
    st.write(f"Você selecionou: {option}")
    
    st.write("#### Teste de expander")
    with st.expander("Clique para expandir"):
        st.write("Conteúdo do expander está funcionando!")
    
    st.info("Se todos os testes acima funcionarem corretamente, o problema não está nos componentes básicos do Streamlit.")
    
    # Informações de diagnóstico
    st.write("### Informações do Sistema")
    st.code(f"""
Python version: {os.popen('python --version').read().strip()}
Streamlit version: {st.__version__}
Working directory: {os.getcwd()}
    """)

if __name__ == "__main__":
    main()