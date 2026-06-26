#!/usr/bin/env python3
# ********************************************************************************************************
# * Empresa        : SI Sistemas Inteligentes
# * Script         : run_dashboard.py
# * Programador    : Sistema de IA
# * Linguagem      : Python
# * Objetivo       : Executar dashboard web externamente
# * Data Criação   : 27/01/2026
# ********************************************************************************************************

import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Importa o app
from web_server import app, db_service

if __name__ == '__main__':
    # Banner
    print("=" * 80)
    print("   Netquadras - Eventos Viaweb - Dashboard Web")
    print("   CM Project Sistemas Inteligentes Eletrônicos")
    print("=" * 80)
    print()
    
    # Conecta ao banco
    print("[Dashboard] Conectando ao banco de dados...")
    if db_service.connect():
        print("[Dashboard] ✓ Banco de dados conectado com sucesso!")
    else:
        print("[Dashboard] ✗ ERRO: Não foi possível conectar ao banco de dados")
        print("[Dashboard] Verifique as credenciais no arquivo .env")
    
    print()
    print("[Dashboard] Servidor iniciando na porta 5000...")
    print("[Dashboard] Acesse:")
    print()
    print("   Local:    http://localhost:5000")
    print("   Rede:     http://0.0.0.0:5000")
    print()
    print("[Dashboard] Pressione Ctrl+C para encerrar")
    print("=" * 80)
    print()
    
    # Executa o servidor
    try:
        app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)
    except KeyboardInterrupt:
        print()
        print("[Dashboard] Encerrando servidor...")
        db_service.disconnect()
        print("[Dashboard] Servidor encerrado com sucesso!")
