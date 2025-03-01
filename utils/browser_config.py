import os
from browser_use import BrowserConfig, Controller
from browser_use.browser.context import BrowserContextConfig

def get_browser_config(browser_config_dict):
    """
    Cria uma configuração otimizada para o navegador em ambientes de produção e desenvolvimento
    """
    # Detectar se estamos em ambiente de produção (Railway)
    is_production = os.environ.get('RAILWAY_ENVIRONMENT') or os.environ.get('PORT')
    
    # Configurar o contexto do navegador
    context_config = BrowserContextConfig(
        browser_window_size={
            'width': browser_config_dict.get('browser_window_width', 1280), 
            'height': browser_config_dict.get('browser_window_height', 1100)
        },
        highlight_elements=browser_config_dict.get('highlight_elements', True),
    )
    
    # Em produção, forçar configurações otimizadas
    if is_production:
        browser_conf = BrowserConfig(
            headless=True,  # Forçar headless em produção
            disable_security=True,
            new_context_config=context_config,
            extra_chromium_args=[
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--disable-setuid-sandbox',
                '--disable-software-rasterizer'
            ]
        )
    else:
        # Em desenvolvimento, usar as configurações do usuário
        browser_conf = BrowserConfig(
            headless=browser_config_dict.get('headless', False),
            disable_security=browser_config_dict.get('disable_security', True),
            new_context_config=context_config,
            chrome_instance_path=browser_config_dict.get('chrome_instance_path')
        )
    
    return browser_conf

def create_controller_with_retry():
    """
    Cria um controlador com mecanismo de retry para ambientes de produção
    """
    controller = Controller()
    
    # Adicionar ação customizada para retry em caso de falha
    @controller.action('Retry failed action')
    async def retry_action(action_name: str, params: dict, max_attempts: int = 3):
        """Tenta executar uma ação várias vezes em caso de falha"""
        attempts = 0
        last_error = None
        
        while attempts < max_attempts:
            try:
                # Executar a ação desejada
                result = await getattr(controller, action_name)(**params)
                return result
            except Exception as e:
                attempts += 1
                last_error = str(e)
                await asyncio.sleep(1)  # Esperar 1 segundo antes de tentar novamente
        
        return f"Falha após {max_attempts} tentativas. Último erro: {last_error}"
    
    return controller