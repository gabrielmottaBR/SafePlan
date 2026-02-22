#!/usr/bin/env python3
"""
Setup script para configurar credenciais do PI Server automaticamente.

Este script:
1. Obtém automaticamente o username Windows do usuário logado
2. Solicita a senha do PI Server de forma segura
3. Salva as credenciais no arquivo .env para uso posterior

Uso:
    python scripts/setup_credentials.py
"""

import os
import sys
import getpass
from pathlib import Path
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
ENV_FILE = PROJECT_ROOT / '.env'
ENV_EXAMPLE = PROJECT_ROOT / '.env.example'


def get_windows_username():
    """Obtém automatically o username do Windows logado."""
    try:
        import getpass
        username = getpass.getuser()
        return username
    except Exception as e:
        logger.error(f"Erro ao obter username Windows: {e}")
        return None


def read_current_env():
    """Lê arquivo .env atual preservando outras configurações."""
    if not ENV_FILE.exists():
        # Se não existe, copia do template
        if ENV_EXAMPLE.exists():
            with open(ENV_EXAMPLE, 'r', encoding='utf-8') as f:
                return f.read()
        return ""
    
    with open(ENV_FILE, 'r', encoding='utf-8') as f:
        return f.read()


def update_env_credentials(content: str, username: str, password: str) -> str:
    """Atualiza as credenciais no conteúdo do .env."""
    lines = content.split('\n')
    updated_lines = []
    
    username_found = False
    password_found = False
    
    for line in lines:
        # Atualizar ou adicionar USERNAME
        if line.startswith('PI_SERVER_USERNAME='):
            updated_lines.append(f"PI_SERVER_USERNAME={username}")
            username_found = True
        # Atualizar ou adicionar PASSWORD
        elif line.startswith('PI_SERVER_PASSWORD='):
            updated_lines.append(f"PI_SERVER_PASSWORD={password}")
            password_found = True
        else:
            updated_lines.append(line)
    
    # Se não encontrou, adicionar no final
    if not username_found:
        updated_lines.insert(2, f"PI_SERVER_USERNAME={username}")
    if not password_found:
        updated_lines.insert(3, f"PI_SERVER_PASSWORD={password}")
    
    return '\n'.join(updated_lines)


def save_env(content: str):
    """Salva o conteúdo no arquivo .env."""
    with open(ENV_FILE, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Definir permissões restritivas (apenas leitura para owner)
    os.chmod(ENV_FILE, 0o600)


def validate_env():
    """Valida se as credenciais foram configuradas."""
    load_dotenv(ENV_FILE)
    
    username = os.getenv('PI_SERVER_USERNAME')
    password = os.getenv('PI_SERVER_PASSWORD')
    
    if not username or not password:
        logger.error("❌ Credenciais não estão completas no .env")
        return False
    
    logger.info(f"✓ Username: {username}")
    logger.info(f"✓ Password: {'*' * len(password)}")
    return True


def main():
    """Função principal."""
    print("\n" + "="*70)
    print("SafePlan - Configuração de Credenciais do PI Server")
    print("="*70 + "\n")
    
    # 1. Obter username Windows
    logger.info("📋 Detectando username Windows...")
    windows_user = get_windows_username()
    
    if not windows_user:
        logger.error("❌ Não foi possível obter o username do Windows")
        return False
    
    logger.info(f"✓ Username Windows detectado: {windows_user}\n")
    
    # 2. Oferecer opção de usar username Windows ou digitar outro
    logger.info("Opções:")
    logger.info("  1. Usar username Windows automaticamente")
    logger.info("  2. Digitar username diferente (ex: para autenticação de domínio)")
    
    choice = input("\nEscolha uma opção (1 ou 2) [padrão: 1]: ").strip() or "1"
    
    if choice == "2":
        username = input("Digite o username para PI Server: ").strip()
        if not username:
            logger.error("❌ Username não pode estar vazio")
            return False
    else:
        username = windows_user
    
    logger.info(f"\nUsername a usar: {username}\n")
    
    # 3. Solicitar senha de forma segura
    logger.info("🔐 Digite a senha para o PI Server (não será exibida):")
    password = getpass.getpass("Senha: ")
    
    if not password:
        logger.error("❌ Senha não pode estar vazia")
        return False
    
    # 4. Confirmar senha
    logger.info("Confirme a senha:")
    password_confirm = getpass.getpass("Senha (novamente): ")
    
    if password != password_confirm:
        logger.error("❌ As senhas não correspondem")
        return False
    
    logger.info("✓ Senhas correspondem\n")
    
    # 5. Atualizar arquivo .env
    logger.info("💾 Salvando credenciais no .env...")
    
    current_content = read_current_env()
    updated_content = update_env_credentials(current_content, username, password)
    save_env(updated_content)
    
    logger.info(f"✓ Arquivo .env atualizado: {ENV_FILE}\n")
    
    # 6. Validar
    logger.info("✓ Validando configuração...")
    if not validate_env():
        return False
    
    print("\n" + "="*70)
    logger.info("✅ Credenciais configuradas com sucesso!")
    print("="*70)
    
    logger.info("\n📝 Próximos passos:")
    logger.info("  1. Inicializar banco de dados:")
    logger.info("     python scripts/init_db.py")
    logger.info("  2. Descobrir sensores do PI AF:")
    logger.info("     python scripts/discover_sensors_from_af.py")
    logger.info("  3. Importar sensores para banco:")
    logger.info("     python scripts/import_sensors_from_buzios.py")
    logger.info("  4. Iniciar dashboard:")
    logger.info("     streamlit run app/main.py")
    logger.info("")
    
    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\n\n⚠️ Configuração cancelada pelo usuário")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n❌ Erro: {e}")
        sys.exit(1)
